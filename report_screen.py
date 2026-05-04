# report_screen.py - Report Item Screen

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from constants import BG, ACCENT, BTN_SEC_BG, FONT_HEAD, FONT_BODY, FONT_SMALL, PAD
from constants import make_banner, styled_btn
import database as db
import notifications_onesignal as notify


class ReportScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._image_path = None
        self._build()

    def _build(self):
        make_banner(self, "📝  Report a Lost / Found Item")

        # Back button
        tk.Button(self, text="← Back to Home", font=FONT_SMALL,
                  bg=BG, fg=ACCENT, relief="flat", cursor="hand2",
                  command=self.controller.show_home).pack(anchor="w", padx=PAD*2, pady=(6, 0))

        # Scrollable form container
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.form_frame = tk.Frame(canvas, bg=BG)
        canvas_window = canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        def on_resize(e):
            canvas.itemconfig(canvas_window, width=e.width)
        canvas.bind("<Configure>", on_resize)
        self.form_frame.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frm = self.form_frame
        col_pad = PAD * 3

        def row_label(text):
            tk.Label(frm, text=text, font=FONT_HEAD, bg=BG, anchor="w").pack(
                fill="x", padx=col_pad, pady=(8, 0))

        # Report type
        row_label("Report Type:")
        rtype_frm = tk.Frame(frm, bg=BG)
        rtype_frm.pack(fill="x", padx=col_pad)
        self.rtype_var = tk.StringVar(value="Lost")
        for val, label in [("Lost", "  I Lost this Item  "), ("Found", "  I Found this Item  ")]:
            tk.Radiobutton(rtype_frm, text=label, variable=self.rtype_var, value=val,
                           font=FONT_BODY, bg=BG, activebackground=BG).pack(side="left")

        # Item name
        row_label("Item Name:  *")
        self.name_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.name_var, font=FONT_BODY, width=50).pack(
            fill="x", padx=col_pad)

        # Category
        row_label("Category:  *")
        self.cat_var = tk.StringVar(value=db.CATEGORIES[0])
        ttk.Combobox(frm, textvariable=self.cat_var, values=db.CATEGORIES,
                     state="readonly", font=FONT_BODY).pack(fill="x", padx=col_pad)

        # Description
        row_label("Description:")
        self.desc_text = tk.Text(frm, font=FONT_BODY, height=4, relief="solid", bd=1)
        self.desc_text.pack(fill="x", padx=col_pad)

        # Location
        row_label("Location:  *")
        self.loc_var = tk.StringVar(value=db.LOCATIONS[0])
        ttk.Combobox(frm, textvariable=self.loc_var, values=db.LOCATIONS,
                     state="readonly", font=FONT_BODY).pack(fill="x", padx=col_pad)

        # Date
        row_label("Date:  *")
        self.date_var = tk.StringVar(value=str(date.today()))
        tk.Entry(frm, textvariable=self.date_var, font=FONT_BODY, width=20).pack(
            anchor="w", padx=col_pad)
        tk.Label(frm, text="(auto-filled — edit if needed, format: YYYY-MM-DD)",
                 font=FONT_SMALL, bg=BG, fg="gray").pack(anchor="w", padx=col_pad)

        # Upload image
        img_frm = tk.Frame(frm, bg=BG)
        img_frm.pack(fill="x", padx=col_pad, pady=(4, 0))
        styled_btn(img_frm, "📷  Upload Image (optional)", self._upload_image,
                   bg=BTN_SEC_BG).pack(side="left")
        self.img_label = tk.Label(img_frm, text="No image selected", font=FONT_SMALL,
                                  bg=BG, fg="gray")
        self.img_label.pack(side="left", padx=8)

        # Submit and Clear buttons
        btn_frm = tk.Frame(frm, bg=BG)
        btn_frm.pack(fill="x", padx=col_pad, pady=16)
        styled_btn(btn_frm, "✅  Submit Report", self._submit).pack(side="left", padx=4)
        styled_btn(btn_frm, "🔄  Clear / Reset", self._clear, bg=BTN_SEC_BG).pack(side="left", padx=4)
        styled_btn(btn_frm, "← Home", self.controller.show_home, bg=BTN_SEC_BG).pack(side="right", padx=4)

    # Actions
    def _upload_image(self):
        path = filedialog.askopenfilename(
            title="Select Item Photo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if path:
            self._image_path = path
            self.img_label.config(text=path.split("/")[-1], fg="green")

    def _submit(self):
        # Validation - check required fields
        missing = []
        if not self.name_var.get().strip():
            missing.append("Item Name")
        if not self.loc_var.get().strip():
            missing.append("Location")
        if not self.date_var.get().strip():
            missing.append("Date")
        if missing:
            messagebox.showerror("Missing Required Fields",
                                 "Please fill in:\n• " + "\n• ".join(missing))
            return

        report_type = self.rtype_var.get()
        item_name   = self.name_var.get().strip()
        category    = self.cat_var.get()
        description = self.desc_text.get("1.0", tk.END).strip()
        location    = self.loc_var.get()
        date_val    = self.date_var.get().strip()
        image_path  = self._image_path

         # Saving to database
        db.insert_report(report_type, item_name, category,
                         description, location, date_val, image_path)

        # Broadcast OneSignal notification to all users in the background
        notify.notify_new_report(report_type, item_name, location)

        messagebox.showinfo("Success", "Report submitted successfully!")
        self._clear()
        self.controller.show_home()

    def _clear(self):
        self.name_var.set("")
        self.cat_var.set(db.CATEGORIES[0])
        self.desc_text.delete("1.0", tk.END)
        self.loc_var.set(db.LOCATIONS[0])
        self.date_var.set(str(date.today()))
        self._image_path = None
        self.img_label.config(text="No image selected", fg="gray")

    # Pre-set the report type (called from Home screen buttons)
    def set_report_type(self, rtype):
        self.rtype_var.set(rtype)
