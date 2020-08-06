import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from pathlib import Path
import bcrypt


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Welcome to the manual labeling tool by Kilian Schnelle\n", font=controller.heading_style)
        label.grid(row=0, column=0, columnspan=2)

        login_label = tk.Label(self, text="Username:", font=controller.heading_style)
        login_label.grid(row=1, column=0, sticky='e')
        self.login_entry = tk.Entry(self)
        self.login_entry.grid(row=1, column=1, sticky='w')

        new_user_button = tk.Button(self, text="Create new user", command=self.create_new_user)
        new_user_button.grid(row=2, column=1, sticky='w')

        login_button = tk.Button(self, text="Login", command=self.login)
        login_button.grid(row=2, column=0, sticky='e')

        controller.bind('<Return>', self.login)

    def login(self, event=None):
        user = self.login_entry.get()
        if user not in self.get_user_list():
            messagebox.showinfo("Warning", "The user " + user + " does not exist. ", icon="warning")
            return
        with Path(self.controller.folder / "users/logins.txt").open("r") as inp:
            for line in inp:
                if line.startswith(user):
                    hash_and_salt = line.split()[1]
        while True:
            password = simpledialog.askstring("Password", "Type in your password")
            if password is None:
                messagebox.showinfo("Abort", "User creation aborted. You will now return to the login screen. ")
                return
            if bcrypt.checkpw(password.encode(), hash_and_salt.encode()) is True:
                break
            else:
                messagebox.showinfo("Warning", "Password is not correct. ", icon="warning")
        self.controller.current_user.set(user)
        self.controller.unbind('<Return>')
        self.controller.show_frame("MainPage")

    def create_new_user(self):
        while True:
            user = simpledialog.askstring("Username", "Type in the new username")
            if user in self.get_user_list():
                messagebox.showinfo("Warning", "The user " + user + " already exists. ", icon="warning")
            else:
                break
        if user is None:
            messagebox.showinfo("Abort", "User creation aborted. You will now return to the login screen. ")
            return
        while True:
            password = simpledialog.askstring("Password", "Type in the new password")
            if password is None:
                messagebox.showinfo("Abort", "User creation aborted. You will now return to the login screen. ")
                return
            password_rep = simpledialog.askstring("Repeat Password", "Please repeat your password")
            if password_rep is None:
                messagebox.showinfo("Abort", "User creation aborted. You will now return to the login screen. ")
                return
            elif password != password_rep:
                messagebox.showinfo("Warning", "The passwords did not match. ", icon="warning")
                continue
            else:
                break
        hash_and_salt = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        with Path(self.controller.folder / "users/logins.txt").open("a") as out:
            out.write(user + " " + hash_and_salt.decode() + "\n")
        user_folder = Path(self.controller.folder / "users/{}".format(user))
        user_folder.mkdir(exist_ok=False)
        Path(user_folder / "projects").mkdir()
        Path(user_folder / "config.pickle").touch()
        self.controller.current_user.set(user)
        self.controller.unbind('<Return>')
        self.controller.show_frame("MainPage")

    def get_user_list(self):
        return [i.name for i in Path(self.controller.folder / "users").glob("*") if i.is_dir()]






