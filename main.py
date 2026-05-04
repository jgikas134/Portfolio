# main.py - CCSU Lost & Found Campus Application
# MIS 310 | Group 8 | Spring 2026

import tkinter as tk
import database as db
from home_screen import HomeScreen
from report_screen import ReportScreen


# App controller
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CCSU Lost & Found")
        self.geometry("700x600")
        self.minsize(600, 500)

        # Initialize database
        db.init_db()

        # Create screens
        self._screens = {}
        for ScreenClass in (HomeScreen, ReportScreen):
            frame = ScreenClass(self, self)
            self._screens[ScreenClass.__name__] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_home()

    # Navigation
    def _show(self, name):
        self._screens[name].tkraise()

    def show_home(self):
        self._screens["HomeScreen"].refresh()
        self._show("HomeScreen")

    def show_report(self, report_type="Lost"):
        self._screens["ReportScreen"].set_report_type(report_type)
        self._show("ReportScreen")


# Entry point
if __name__ == "__main__":
    app = App()
    app.mainloop()
