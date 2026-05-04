# home_screen.py - Home / Search Screen

import tkinter as tk
from tkinter import messagebox
from constants import BG, ACCENT, BTN_SEC_BG, FONT_HEAD, FONT_BODY, FONT_SMALL, PAD
from constants import make_banner, styled_btn, format_row
import database as db

# Algolia smart search for a fallback if not installed
try:
    from algoliasearch.search_client import SearchClient
    from config import ALGOLIA_APP_ID, ALGOLIA_SEARCH_KEY, ALGOLIA_INDEX_NAME

    _algolia_index = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SEARCH_KEY) \
        .init_index(ALGOLIA_INDEX_NAME)
    ALGOLIA_ON = True
except Exception:
    _algolia_index = None
    ALGOLIA_ON = False

# OpenAI matching fallback if key not set
try:
    from config import OPENAI_API_KEY
    import openai_service

    OPENAI_ON = OPENAI_API_KEY != "YOUR_OPENAI_API_KEY"
except Exception:
    OPENAI_ON = False

def _algolia_search(keyword, report_type=None):
    """Query Algolia; return list of report dicts or None on failure."""
    try:
        params = {"hitsPerPage": 50}
        if report_type:
            params["filters"] = f"report_type:{report_type}"
        hits = _algolia_index.search(keyword, params).get("hits", [])
        return [{
            "id":          h.get("id") or h.get("objectID"),
            "report_type": h.get("report_type", ""),
            "item_name":   h.get("item_name", ""),
            "category":    h.get("category", ""),
            "description": h.get("description", ""),
            "location":    h.get("location", ""),
            "date":        h.get("date", ""),
            "image_path":  h.get("image_path"),
            "created_at":  h.get("created_at", ""),
        } for h in hits]
    except Exception as e:
        print(f"[Algolia] search error: {e}")
        return None

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._build()

    def _build(self):
        make_banner(self, "🎓  LOST & FOUND — CCSU Campus Application")

        # Algolia status badge
        badge_text  = "🔍 Smart Search: ON (Algolia)" if ALGOLIA_ON \
                      else "🔍 Smart Search: OFF (local fallback)"
        badge_color = "#006400" if ALGOLIA_ON else "#888888"
        tk.Label(self, text=badge_text, font=FONT_SMALL, bg=BG,
                 fg=badge_color).pack(anchor="e", padx=PAD*2, pady=(4, 0))

        # Mode selector
        mode_frm = tk.Frame(self, bg=BG)
        mode_frm.pack(fill="x", padx=PAD*2, pady=(PAD, 0))
        tk.Label(mode_frm, text="Mode:", font=FONT_HEAD, bg=BG).pack(side="left")
        self.mode_var = tk.StringVar(value="Lost")
        for val, label in [("Lost", "  I Lost an Item  "), ("Found", "  I Found an Item  ")]:
            tk.Radiobutton(mode_frm, text=label, variable=self.mode_var, value=val,
                           font=FONT_BODY, bg=BG, activebackground=BG).pack(side="left", padx=8)

        # Search bar
        search_frm = tk.Frame(self, bg=BG)
        search_frm.pack(fill="x", padx=PAD*2, pady=(6, 0))
        tk.Label(search_frm, text="Search:", font=FONT_HEAD, bg=BG).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frm, textvariable=self.search_var,
                                     font=FONT_BODY, width=45)
        self.search_entry.pack(side="left", padx=(8, 4))
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        # Action buttons
        btn_frm = tk.Frame(self, bg=BG)
        btn_frm.pack(fill="x", padx=PAD*2, pady=8)
        styled_btn(btn_frm, "🔍  Search / Find Match", self._do_search).pack(side="left", padx=4)
        styled_btn(btn_frm, "📋  View All Reports", self._view_all,
                   bg=BTN_SEC_BG).pack(side="left", padx=4)

        # AI Match button
        ai_color = BTN_BG if OPENAI_ON else BTN_SEC_BG
        self.ai_btn = styled_btn(btn_frm, "🤖  AI Match", self._do_ai_match, bg=ai_color)
        self.ai_btn.pack(side="left", padx=4)
        if not OPENAI_ON:
            self.ai_btn.config(state="disabled")

        # Results label
        self.results_label = tk.Label(self, text="Results:", font=FONT_HEAD, bg=BG, anchor="w")
        self.results_label.pack(fill="x", padx=PAD*2)

        # Results listbox
        list_frm = tk.Frame(self, bg=BG)
        list_frm.pack(fill="both", expand=True, padx=PAD*2, pady=4)

        scrollbar = tk.Scrollbar(list_frm)
        scrollbar.pack(side="right", fill="y")

        self.results_box = tk.Listbox(list_frm, font=FONT_BODY, yscrollcommand=scrollbar.set,
                                      selectbackground=ACCENT, selectforeground="white",
                                      height=12, bg="white", relief="solid", bd=1)
        self.results_box.pack(fill="both", expand=True)
        scrollbar.config(command=self.results_box.yview)
        self.results_box.bind("<Double-Button-1>", self._on_result_select)

        tk.Label(self, text="(double-click a result to see details)",
                 font=FONT_SMALL, bg=BG, fg="gray").pack(anchor="w", padx=PAD*2)

        # Bottom navigation
        nav_frm = tk.Frame(self, bg=BG)
        nav_frm.pack(fill="x", padx=PAD*2, pady=PAD)
        styled_btn(nav_frm, "📝  Report a Lost Item",
                   lambda: self.controller.show_report("Lost")).pack(side="left", padx=4)
        styled_btn(nav_frm, "📝  Report a Found Item",
                   lambda: self.controller.show_report("Found")).pack(side="left", padx=4)

    # Search and display results
    def _do_search(self):
        keyword = self.search_var.get().strip()
        mode = self.mode_var.get()

        if ALGOLIA_ON:
            results = _algolia_search(keyword, report_type=mode)
            if results is not None:
                self._display_results(results, source="algolia")
                return

        results = db.search_reports(keyword, report_type=mode)
        self._display_results(results, source="local")

    def _view_all(self):
        results = db.get_all_reports()
        self._display_results(results)

    #AI Match logic

    def _do_ai_match(self):
        """
        Takes the keyword in the search bar as the lost item name,
        finds its DB record, then sends it + all found reports to OpenAI.
        Displays results ranked by match score.
        """
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning("AI Match",
                                   "Type the name of your lost item in the search bar first.")
            return

        # Find the lost report to match against
        lost_results = db.search_reports(keyword, report_type="Lost")
        if not lost_results:
            messagebox.showinfo("AI Match",
                                "No lost report found for that item. Submit a report first.")
            return

        lost_report = lost_results[0]  # use the most recent match
        found_reports = db.get_all_reports(report_type="Found")

        if not found_reports:
            messagebox.showinfo("AI Match", "No found items in the system yet.")
            return

        # Show a loading message while GPT works
        self.results_label.config(text="🤖  AI Match running... please wait")
        self.update_idletasks()

        # Call OpenAI — line 143 in openai_service.py does the actual API call
        matches = openai_service.find_matches(lost_report, found_reports)

        if not matches:
            self.results_label.config(text="Results:")
            messagebox.showerror("AI Match",
                                 "OpenAI did not return results. Check your API key in config.py.")
            return

        self._display_ai_results(matches)

    def _display_ai_results(self, matches):
        """Show AI-scored matches in the listbox with score + reason."""
        self.results_box.delete(0, tk.END)
        self._current_results = matches
        self.results_label.config(
            text=f"🤖  AI Match Results  ({len(matches)} found items ranked by similarity):")

        for r in matches:
            score = r.get("match_score", 0)
            reason = r.get("match_reason", "")
            base = format_row(r)
            line = f"  [{score:>3}%]  {base}  |  {reason}"
            self.results_box.insert(tk.END, line)


    def _display_results(self, results, source="local"):
        self.results_box.delete(0, tk.END)
        self._current_results = results

        if source == "algolia":
            self.results_label.config(
                text=f"Results  (Algolia smart search — {len(results)} found):")
        else:
            self.results_label.config(text=f"Results  ({len(results)} found):")

        if not results:
            self.results_box.insert(tk.END, "  No results found.")
        else:
            for r in results:
                self.results_box.insert(tk.END, "  " + format_row(r))

    def _on_result_select(self, _event):
        sel = self.results_box.curselection()
        if not sel or not hasattr(self, "_current_results"):
            return
        idx = sel[0]
        if idx >= len(self._current_results):
            return
        record = self._current_results[idx]
        self.controller.show_match([record], detail=True)

    def refresh(self):
        self.results_box.delete(0, tk.END)
        self.results_label.config(text="Results:")