# constants.py - Shared colors, fonts, and helper widgets

import tkinter as tk

# Colors
BG         = "#f0f4f8"
BANNER_BG  = "#003366"
BANNER_FG  = "#ffffff"
ACCENT     = "#003366"
BTN_BG     = "#003366"
BTN_FG     = "#ffffff"
BTN_SEC_BG = "#6c757d"

# Fonts
FONT_TITLE = ("Helvetica", 16, "bold")
FONT_HEAD  = ("Helvetica", 11, "bold")
FONT_BODY  = ("Helvetica", 10)
FONT_SMALL = ("Helvetica", 9)

# Padding
PAD = 10


# Create a banner at the top of each screen
def make_banner(parent, text):
    frm = tk.Frame(parent, bg=BANNER_BG)
    frm.pack(fill="x")
    tk.Label(frm, text=text, font=FONT_TITLE, bg=BANNER_BG, fg=BANNER_FG,
             pady=12).pack()
    return frm


# Create a styled button
def styled_btn(parent, text, command, bg=BTN_BG, fg=BTN_FG, **kw):
    return tk.Button(parent, text=text, command=command,
                     bg=bg, fg=fg, font=FONT_BODY,
                     relief="flat", padx=12, pady=6,
                     activebackground="#004080", activeforeground=fg,
                     cursor="hand2", **kw)


# Format a report dict as a single listbox line
def format_row(r):
    tag = "[LOST]" if r["report_type"] == "Lost" else "[FOUND]"
    return f"{tag}  {r['item_name']:<30}  {r['location']:<20}  {r['date']}"
