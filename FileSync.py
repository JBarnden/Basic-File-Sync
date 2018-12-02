"""
Basic File Sync v0.1.0

Description:
Cross-platform File Sync program that copies source file/directory (from file) to the destination file/directory (to file) when changes are detected.
This is a hugely basic, quickly written version that needs some serious improving.  It's currently limited to working
only with single files or directories.

In future I hope to support:
- Multiple to & from files 
- menu for saving and loading configuration and an application
- maintained, user accessible log.

Author:
James Barnden

License:
MIT

"""

import os
from shutil import copyfile
from shutil import Error as shutilError
from distutils.dir_util import copy_tree
import tkinter as tk
from tkinter import filedialog
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import datetime
import pickle

class FileEventHandler(PatternMatchingEventHandler):
    """
    An event handler to listen to the file at the given from_file path, copying its contents to the given to_file path.
    """
    patterns = None
    def __init__(self, to_file, from_file, status_text, patterns=None):
        """
        Stores and initializes from_file, to_file and the variable used to track the current status
        """
        super().__init__(patterns=self.patterns)
        self.to_file = to_file
        self.from_file = from_file
        self.status_text = status_text

    def on_modified(self, otherParam):
        """
        Callback method is called when a change is detected in the file at path 'from_file'
        """
        try:
            print("Change detected copying file")
            updateString = "Change detected, files synced: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if os.path.isfile(self.from_file) and os.path.isfile(self.to_file):
                # We're working with files, Update to_file
                copyfile(self.from_file, self.to_file)
                self.status_text.set(updateString)
            elif os.path.isdir(self.from_file) and os.path.isdir(self.to_file):
                # We're working with directories, Update to_file
                copy_tree(self.from_file, self.to_file)
                self.status_text.set(updateString)
        except(shutilError, OSError, IOError):
            print("Failed to copy file")
            updateString = "Failed to copy file: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_text.set(updateString)

class Application(tk.Frame):
    """
    Main application class
    """

    def __init__(self, master=None):
        """
        Initializes application variables, creates GUI widgets, and loads config (if detected)
        """
        super().__init__(master)
        self.default_config_path = "file_sync_config.p"
        self.from_path = ''
        self.to_path = ''
        self.sync_when_start = tk.IntVar()

        self.status_text = tk.StringVar()
        self.status_text.set("Ready & waiting")

        self.master = master
        self.pack()
        self.create_widgets()
        self.load_config(self.default_config_path)
    
    def load_config(self, path):
        """
        Load previously saved configuration
        """
        if not os.path.isfile(path): return
        config = pickle.load(open(path, "rb"))

        self.from_path = config["from_path"]
        fromTxt = tk.StringVar()
        self.from_path_entry["textvariable"] = fromTxt
        fromTxt.set(self.from_path)
        self.to_path = config["to_path"]
        toTxt = tk.StringVar()
        self.to_path_entry["textvariable"] = toTxt
        toTxt.set(self.to_path)

        self.sync_when_start.set(config["sync_when_start"])
        self.auto_sync.variable = self.sync_when_start
        if self.sync_when_start.get():
            self.start_sync()

    def save_config(self, path):
        """
        Saves currently set to and from paths
        """
        config = {
            "from_path": self.from_path,
            "to_path": self.to_path,
            "sync_when_start": self.sync_when_start.get()
        }
        pickle.dump(config, open(path, "wb"))
        self.status_text.set("Configuration saved")

    def create_widgets(self):
        """
        Method responsible for creating and initializing all GUI widgets
        """
        rowNo = 0

        self.auto_sync = tk.Checkbutton(self, text="Start Syncing when app starts", variable=self.sync_when_start)
        self.auto_sync.grid(column=0, row=rowNo)
        rowNo+=1

        lbl_from_path = tk.Label(self, text="From path: ")
        lbl_from_path.grid(column=0, row=rowNo)
        rowNo+=1

        self.from_path_entry = tk.Entry(self, width="50", state='disabled')
        self.from_path_entry.grid(column=0, row=rowNo)

        self.btn_from_browse = tk.Button(self, text="...", command = lambda: self.store_path('from'))
        self.btn_from_browse.grid(column=1, row=rowNo)
        rowNo+=1

        lbl_to_path = tk.Label(self, text="To path: ")
        lbl_to_path.grid(column=0, row=rowNo)
        rowNo+=1

        self.to_path_entry = tk.Entry(self, width="50", state='disabled')
        self.to_path_entry.grid(column=0, row=rowNo)

        self.btn_to_browse = tk.Button(self, text="...", command=lambda: self.store_path('to'))
        self.btn_to_browse.grid(column=1, row=rowNo)
        rowNo+=1

        self.lbl_status = tk.Label(self, text="Status: ")
        self.lbl_status.grid(column=0, row=rowNo)
        rowNo+=1
        self.status_box = tk.Entry(self, width="50", state='disabled')
        self.status_box["textvariable"] = self.status_text
        self.status_box.grid(column=0, row=rowNo)
        rowNo+=1

        self.btn_start_sync = tk.Button(self, text="Start Sync", fg="green", command=self.start_sync)
        self.btn_start_sync["state"] = "active"
        self.btn_start_sync.grid(column=0, row=rowNo)

        self.btn_stop_sync = tk.Button(self, text="Stop Sync", command=self.stop_sync)
        self.btn_stop_sync["state"] = "disabled"
        self.btn_stop_sync.grid(column=1, row=rowNo)

        self.btn_save = tk.Button(self, text="Save", command=lambda: self.save_config(self.default_config_path))
        self.btn_save.grid(column=3, row=rowNo)

        self.btn_quit = tk.Button(self, text="Quit", fg="red",
                              command=self.master.destroy)
        self.btn_quit.grid(column=2, row=rowNo)

    def store_path(self, from_or_to):
        """
        This function currently sucks, need to find a way to be able to set variable values through a lambda
        (updating self.from_path passed in via lambda didn't work)
        """
        path = tk.filedialog.askopenfilename(initialdir = "~", title="Choose file to listen to for changes" )
        if from_or_to == 'from':
            self.from_path = path
            fromTxt = tk.StringVar()
            self.from_path_entry["textvariable"] = fromTxt
            fromTxt.set(path)
        elif from_or_to == 'to':
            self.to_path = path
            toTxt = tk.StringVar()
            self.to_path_entry["textvariable"] = toTxt
            toTxt.set(path)
        else:
            self.status_text.set("The rubbish method kicked off")
        

    def start_sync(self):
        """
        Function populates and starts and initializes an event handler and observer combo.
        """
        if not self.validate_input(): return

        print("Start sync from: '", self.from_path, "', to '", self.to_path, "'")
        self.btn_start_sync["state"] = "disabled"
        
        # Set up FileEventHandler
        e_h = FileEventHandler(to_file=self.to_path, from_file=self.from_path, status_text=self.status_text, patterns=self.from_path)

        # Start observer
        basePath, filename = os.path.split(self.from_path)

        self.observer = Observer()
        self.observer.schedule(e_h, basePath)
        self.observer.start()
        self.status_text.set("Started Listener succesfully...")


        self.btn_stop_sync["state"] = "active"

    def validate_input(self):
        """
        Returns True if input is valid
        """
        errorString = ""
        valid = True

        frm_path, frm_filename = os.path.split(self.from_path)
        t_path, t_filename = os.path.split(self.to_path)

        if self.from_path == '' or self.to_path == '':
            errorString = "You must set both two and from paths"
            valid = False
        if self.from_path == self.to_path:
            print("To and from paths were equal")
            self.status_text.set("To and from paths were equal")
            valid = False
        if not os.path.isdir(frm_path):
            errorString = "From path must be a valid directory"
            valid = False
        if not os.path.isdir(t_path):
            errorString = "To path must be a valid directory"
            valid = False
        if os.path.isfile(frm_filename) and frm_filename != t_filename:
            errorString = "To and from files must have the same name"
        if os.path.isdir(self.from_path) and os.path.isdir(self.to_path) \
            and os.path.basename(os.path.normpath(self.from_path)) != os.path.basename(os.path.normpath(self.to_path)):
            errorString = "To and from directories must have the same name"
            valid = False
        
        print(errorString)
        self.status_text.set(errorString)
        return valid

    def stop_sync(self):
        print("Stop sync")
        self.btn_stop_sync["state"] = "disabled"

        # Stop observer
        self.observer.stop()
        print("Observer stopped")

        self.btn_start_sync["state"] = "active"
        self.status_text.set("Listener stopped.")

root = tk.Tk()
app = Application(master=root)
app.master.title("Basic file sync")
# app.master.geometry('300x300')
app.mainloop()
