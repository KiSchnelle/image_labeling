import tkinter as tk
from pathlib import Path
from gui.LoginPage import LoginPage
from gui.MainPage import MainPage
from tkinter import font


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # self.minsize(500, 500)
        self.heading_style = font.Font(family="Arial", size=16)
        self.small_option_style = font.Font(family="Arial", size=8)
        self.folder = Path(__file__).parents[1]

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.current_user = tk.StringVar()
        self.current_user.set("-")

        self.frames = {}
        for F in (LoginPage, MainPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()



