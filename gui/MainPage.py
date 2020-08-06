import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from tkinter import messagebox


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        creating_message = tk.StringVar()

        welcome_label = tk.Label(self, text="Welcome ", font=self.controller.heading_style)
        welcome_label.grid(row=0, column=0, sticky='e')
        welcome_user = tk.Label(self, textvariable=self.controller.current_user, font=self.controller.heading_style)
        welcome_user.grid(row=0, column=1, sticky='w')

        load_project_button = tk.Button(self, text="Load project", command=self.load_project)
        load_project_button.grid(row=1, column=0)

        new_project_button = tk.Button(self, text="New project")
        new_project_button.grid(row=2, column=0)


    def load_project(self):
        project_folder = Path(self.controller.folder / "users/{}/projects".format(self.controller.current_user.get()))
        if len(tuple(i for i in project_folder.glob("*") if i .is_dir())) == 0:
            messagebox.showinfo("Abort", "No projects found. ")
            return
        load_directory = filedialog.askdirectory(initialdir=project_folder)
        print(load_directory)


