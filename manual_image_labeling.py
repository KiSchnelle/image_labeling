#!/usr/bin/env python

# !! conda environment needs pillow to be installed to use PIL !!
# !! conda environment needs bcrypt to be installed !!

import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
from tkinter import font
import pickle
import time
from copy import deepcopy
from getpass import getpass

try:
    import bcrypt
except ImportError:
    raise RuntimeError("bcrypt package is not installed. ")
try:
    from PIL import ImageTk, Image
except ImportError:
    raise RuntimeError("PIL is not installed, if you are using anaconda you can just install the pillow package. ")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# function for remind of saving when closing main window
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def closing():
    msg_box = messagebox.askquestion("Exit application", "Are you sure you want to exit? Unsaved progress will be lost. ", icon="warning")
    if msg_box == "yes":
        root.destroy()
    else:
        messagebox.showinfo("Return", "You will now return to the application. ")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# setting all the variables
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# uncomment if just every dir in the executing folder and comment the lane after
# image_folders = [i for i in Path.cwd().glob("*") if i.is_dir()]
image_folders = [Path("C:/Users/Kilian-Desktop/Desktop/Gui_Test/1"), Path("C:/Users/Kilian-Desktop/Desktop/Gui_Test/2")]
for i in image_folders:
    if not i.exists():
        raise RuntimeError("The folder " + str(i) + " does not exist. ")

# uncomment if a folder named "results" should be created in executing folder and comment the lane after
# result_folder = Path(Path.cwd() / "results").mkdir(parents=False, exist_ok=False)
result_folder = Path("C:/Users/Kilian-Desktop/Desktop/Gui_Test")
if not result_folder.exists():
    raise RuntimeError("Result folder does not exist. ")

# add any label as string and/or remove existing
labels = ["good", "bad"]

# set resize to False to display original image
# set resize to True to resize image keeping same aspect ratio
resize = True




# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# class for the actual GUI
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class GUI:
    def __init__(self, master, labels, image_folders, result_folder, resize):
        self.master = master
        self.heading_style = font.Font(family="Arial", size=20)

        self.image_folders = image_folders
        self.result_folder = result_folder
        self.resize = resize

        self.labels = labels
        self.index = 0

        self.n_labels = len(labels)

        self.image_dict = {}
        for i in self.image_folders:
            self.image_dict[str(i)] = [str(j) for j in i.glob("*.png")]

        # format: {image_folder: {image_path: label}}
        self.result_dict = {str(i): {str(j): None for j in i.glob("*.png")} for i in self.image_folders}

        self.user = None
        self.vote = None

        self.frames = []

        # ----------SubMenu-----------
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.fileMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="User", menu=self.fileMenu)
        self.fileMenu.add_command(label="New", command=self.new_user)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Load", command=self.load)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Save", command=self.save)
        self.fileMenu.add_command(label="Save & Exit", command=lambda: self.save(exit=True))
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=closing)

        # ----------Frame-------------
        self.main_frame = tk.Frame(self.master)
        self.main_frame.grid()
        self.frames.append(self.main_frame)

        self.user_frame = tk.Frame(self.main_frame)
        self.user_frame.grid(row=0, column=0)
        self.frames.append(self.user_frame)
        tk.Label(self.user_frame, text="Current user: ", font=self.heading_style).grid(row=0, column=0)
        self.current_user = tk.StringVar()
        self.current_user.set("-")
        tk.Label(self.user_frame, textvariable=self.current_user, font=self.heading_style).grid(row=0, column=1)

        tk.Label(self.main_frame, text="Current image folder: ").grid(row=1, column=0)
        self.current_image_folder = tk.StringVar()
        self.current_image_folder.set("-")
        self.file_option_menu = tk.OptionMenu(self.main_frame, self.current_image_folder, *self.image_folders)
        self.file_option_menu.grid(row=1, column=1)
        self.file_scrollbary = tk.Scrollbar(self.main_frame)
        self.file_scrollbary.grid(row=2, column=2, sticky='wns')
        self.file_scrollbarx = tk.Scrollbar(self.main_frame, orient="horizontal")
        self.file_scrollbarx.grid(row=3, column=0, sticky="ew", columnspan=2)
        self.current_image_list = tk.StringVar(value=[])
        self.file_listbox = tk.Listbox(self.main_frame, listvariable=self.current_image_list)
        self.file_listbox.grid(row=2, column=0, sticky='nsew', columnspan=2)
        self.file_scrollbary['command'] = self.file_listbox.yview
        self.file_scrollbarx['command'] = self.file_listbox.xview
        self.file_listbox['yscrollcommand'] = self.file_scrollbary.set
        self.file_listbox['xscrollcommand'] = self.file_scrollbarx.set
        self.current_image_folder.trace("w", self.callback_img_list)

        self.current_image = tk.StringVar()
        self.current_image.set("-")
        self.file_listbox.bind('<<ListboxSelect>>', self.callback_img)

        self.image = None
        self.photo = None
        self.photo_place = tk.Label(self.main_frame)
        self.photo_place.grid(row=2, column=3, sticky='w', columnspan=2)
        tk.Label(self.main_frame, textvariable=self.current_image, font=self.heading_style).grid(row=3, column=3, sticky='w')

        self.rating_frame = tk.Frame(self.main_frame)
        self.rating_frame.grid(row=0, column=3)
        self.frames.append(self.rating_frame)
        tk.Label(self.rating_frame, text="Current rating: ", font=self.heading_style).grid(row=0, column=0)
        self.current_rating = tk.StringVar()
        self.current_rating.set("-")
        tk.Label(self.rating_frame, textvariable=self.current_rating, font=self.heading_style).grid(row=0, column=1,)

        self.voting_toolbar = tk.Frame(self.main_frame, bd=1, relief='raised')
        self.voting_toolbar.grid(row=1, column=3)
        self.frames.append(self.voting_toolbar)
        for i in range(self.n_labels):
            tk.Button(self.voting_toolbar, text=self.labels[i], font=self.heading_style, command=lambda i2=self.labels[i]: self.callback_vote_butt(i2)).grid(row=0, column=i)
            self.master.bind(str(i+1), lambda event, p=i: self.callback_vote_butt(self.labels[p]))

        self.image_toolbar = tk.Frame(self.main_frame, bd=1, relief='raised')
        self.image_toolbar.grid(row=4, column=0, columnspan=2)
        self.frames.append(self.image_toolbar)
        tk.Button(self.image_toolbar, text='previous', command=lambda: self.next_image("minus")).grid(row=0, column=0)
        tk.Button(self.image_toolbar, text='next', command=lambda: self.next_image("plus")).grid(row=0, column=1)
        self.master.bind('<Left>', lambda x: self.next_image("minus"))
        self.master.bind('<Right>', lambda x: self.next_image("plus"))

        # test result button
        tk.Button(self.main_frame, text='Print result', command=self.print_result).grid(row=5, column=0)

    @staticmethod
    def star_file_format(iterableobject):
        returnlist = []
        for x in iterableobject:
            try:
                wert = int(x)
                wertready = "{:12d}".format(wert)
            except ValueError:
                try:
                    wert = float(x)
                    if wert >= 0:
                        wertready = "{:12.6f}".format(wert)
                    else:
                        wertready = "{:12.5f}".format(wert)
                except ValueError:
                    wertready = str(x)
            returnlist.append(wertready)
        return returnlist

    @staticmethod
    def swap_frame(frame):
        frame.tkraise()

    def load_frames(self):
        for i in self.frames:
            i.tkraise()

    def next_image(self, direction):
        select_index = self.file_listbox.curselection()
        next = 0
        if len(select_index) > 0:
            last = int(select_index[-1])
            self.file_listbox.selection_clear(select_index)
            if last < self.file_listbox.size() - 1:
                if direction == "plus":
                    next = last + 1
                elif last > 0 and direction == "minus":
                    next = last - 1
        self.file_listbox.activate(next)
        self.file_listbox.selection_set(next)
        self.callback_img('<<ListboxSelect>>')

    def print_result(self):
        print(self.result_dict)

    def callback_img_list(self, *args):
        if self.user is None:
            self.load()
        self.current_image_list.set(self.image_dict[self.current_image_folder.get()])
        self.current_image.set("-")
        self.image = None
        self.photo = None
        self.photo_place.configure(image=self.photo)

    def callback_img(self, evt):
        self.current_image.set(self.file_listbox.get(self.file_listbox.curselection()))
        self.image = (self.load_image(self.current_image.get()))
        self.photo = ImageTk.PhotoImage(self.image)
        self.photo_place.configure(image=self.photo)
        self.current_rating.set(self.result_dict[self.current_image_folder.get()][self.current_image.get()])

    def callback_vote_butt(self, label):
        self.result_dict[self.current_image_folder.get()][self.current_image.get()] = label
        self.current_rating.set(self.result_dict[self.current_image_folder.get()][self.current_image.get()])

    def load_image(self, image_path):
        image = Image.open(image_path)
        if self.resize is True:
            max_height = 500
            img = image
            s = img.size
            ratio = max_height / s[1]
            image = img.resize((int(s[0]*ratio), int(s[1]*ratio)), Image.ANTIALIAS)
        return image

    def get_user_list(self):
        return [i.stem for i in self.result_folder.glob("*.pickle")]

    def new_user(self):
        if self.user is None:
            while True:
                self.user = simpledialog.askstring("Username", "Type in the new username")
                if self.user in self.get_user_list():
                    messagebox.showinfo("Warning", "The user " + self.user + " already exists. ", icon="warning")
                else:
                    break
            if self.user is None:
                messagebox.showinfo("Abort", "User creation aborted. You will now return to the application. ")
            else:
                with (self.result_folder / "{}.pickle".format(self.user)).open("wb") as out:
                    pickle.dump(obj=deepcopy(self.result_dict), file=out)
                self.current_user.set(self.user)
                messagebox.showinfo("User created", "The user " + self.user + " was created. You will now return to the application. ")
                self.load_frames()
        else:
            msg_box = messagebox.askquestion("A user already loaded", "The user " + self.user + " is already loaded. Do you want to make a new user?")
            if msg_box == "yes":
                msg_box = messagebox.askquestion("Create new user", "Do you want to save progress in user " + self.user + " ?")
                if msg_box == "yes":
                    self.save()
                    self.user = None
                    self.new_user()
                elif msg_box == "no":
                    self.user = None
                    self.new_user()
            else:
                messagebox.showinfo("Return", "You will now return to the application. ")

    def save(self, exit=False):
        if self.user is None:
            messagebox.showinfo("Return", "No user is loaded. You will now return to the application. ")
        else:
            with (self.result_folder / "{}.pickle".format(self.user)).open("wb") as out:
                pickle.dump(obj=deepcopy(self.result_dict), file=out)
            # with (self.result_folder / "{}.star".format(self.user)).open("w") as out:
                # out.write("\ndata_\n\nloop_\n_kiImageFolder #1\n_kiImage #2\n_kiLabel #3\n")
                # or u, o in self.result_dict.items():
                    # for p, q in o.items():
                        # line_list = [str(u), str(p), str(q)]
                        # line_list_ready = self.star_file_format(line_list)
                        # line = " ".join(line_list_ready)
                        # out.write(line + "\n")
            if exit is True:
                messagebox.showinfo("Saved", "Progress for the user " + self.user + " was saved. The application will now quit. ")
                self.master.destroy()
            else:
                messagebox.showinfo("Saved", "Progress for the user " + self.user + " was saved. You will now return to the application. ")

    def load_user(self):
        with (self.result_folder / "{}.pickle".format(self.user)).open("rb") as inp:
            self.result_dict = pickle.load(file=inp)
            messagebox.showinfo("User load", "The user " + self.user + " was loaded. You will now return to the application. ")
            self.current_user.set(self.user)

    def load(self):
        if self.user is None:
            if len(self.get_user_list()) == 0:
                msg_box = messagebox.askquestion("No user found", "No user was found. Do you want to create one?")
                if msg_box == "yes":
                    self.new_user()
                else:
                    messagebox.showinfo("Return", "You will now return to the application. ")
            else:
                options = self.get_user_list()
                options.append("New User")
                msg_box = self.custom_message_box(title=" Choose user", options=options)
            while msg_box is not True:
                time.sleep(1)
            if self.vote == "cancel":
                messagebox.showinfo("Return", "You will now return to the application. ")
                self.vote = None
            else:
                self.user = self.vote
                self.load_user()
                self.vote = None
        else:
            msg_box = messagebox.askquestion("A user already loaded", "The user " + self.user + " is already loaded. Do you want to change to another one?")
            if msg_box == "yes":
                msg_box = messagebox.askquestion("Change user", "Do you want to save progress in user " + self.user + " ?")
                if msg_box == "yes":
                    self.save()
                    self.user = None
                    self.load()
                elif msg_box == "no":
                    self.user = None
                    self.load()
            else:
                messagebox.showinfo("Return", "You will now return to the application. ")

    def set_vote(self, vote, win=None):
        self.vote = vote
        if win is not None:
            win.destroy()

    def custom_message_box(self, title, options, window=None):
        if window is not None:
            window.destroy()
        win = tk.Toplevel()
        win.attributes('-topmost', True)
        win.title(title)
        for i in options:
            tk.Button(win, text=i, command=lambda i2=i: self.set_vote(i2, win)).pack()
        win.protocol("WM_DELETE_WINDOW", lambda: self.set_vote("cancel", win))
        win.wait_window()
        return True


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# starting the GUI
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# start gui
# creating the tk object
root = tk.Tk(className=" Manual labeling tool by Kilian Schnelle")
# uncomment and replace sizes if the window should have a minimum size
# root.minsize(800, 800)

app = GUI(root, labels, image_folders, result_folder,resize)
root.protocol("WM_DELETE_WINDOW", closing)
root.mainloop()


