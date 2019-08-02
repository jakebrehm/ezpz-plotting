# GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from PIL import Image, ImageTk
from lemons import gui

# System packages
import os
import platform

# Plotting packages
import matplotlib
if platform.system() == 'Darwin':
    matplotlib.use("TkAgg") # On Mac, this must come before the pyplot import
import matplotlib.pyplot as plt
if platform.system() == 'Windows':
    matplotlib.use("TkAgg") # On Windows, this must come after the pyplot import
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Data science packages
import math
import numpy as np
import pandas as pd

# Miscellaneous packages
import re
import configobj
import random

# Import custom classes for special types of files
from special import PeakValleyFile


class Application(gui.Application):
    """The main application of the program, which combines the GUI and all related
    methods and functionality."""

    def __init__(self, padding=12):
        """Initialize the main GUI and miscellaneous constants of the program."""

        # Initialize the application using the lemons GUI module
        gui.Application.__init__(self, padding=12)
        self.configure(
            title='EZPZ Plotting',
            icon=gui.ResourcePath('Assets\\icon.ico'),
            resizable=False
        )

        # Initialize program constants
        self.FLIPBOOK = False # keeps track of whether or not the flipbook is open
        self.HELP = False # keeps track of whether or not the help window is open

        # Initialize the inputs list
        self.inputs = []

        # Add a header/logo to the top of the application
        header = gui.Header(self, logo=gui.ResourcePath('Assets\\logo.png'), downscale=10)
        header.grid(row=0, column=0, sticky='NSEW')

        # Add a separator between the header and the listbox
        gui.Separator(self, padding=(0, padding)).grid(row=1, column=0, sticky='NSEW')

        # Add a listbox that will show the users the inputs that have been loaded
        browse_image = gui.RenderImage('Assets\\browse.png', downscale=9)
        self.listbox = gui.InputField(self, quantity='multiple', appearance='list', width=80,
                                 image=browse_image, command=self.browse)
        self.listbox.grid(row=2, column=0, sticky='NSEW')

        # Create a separator between the listbox and the primary frame
        gui.Separator(self, padding=(0, padding)).grid(row=3, column=0, sticky='NSEW')

        # Create the primary frame, where the notebook will be held
        self.primary = tk.Frame(self)
        self.primary.grid(row=4, column=0, sticky='NSEW')
        self.primary.columnconfigure(0, weight=1)
        self.primary.rowconfigure(0, minsize=278)

        # On first load or reset, show a message saying that no inputs have been loaded
        message = 'Please provide at least one input file.\n\nControls will appear here.'
        no_input_label = tk.Label(self.primary, text=message)
        no_input_label.grid(row=0, column=0, sticky='NSEW')

        # Create a separator between the primary frame and the footer
        gui.Separator(self, padding=(0, padding)).grid(row=5, column=0, sticky='NSEW')

        # Create the footer
        footer = tk.Frame(self)
        footer.grid(row=6, column=0, sticky='NSEW')
        footer.columnconfigure(1, weight=1)

        # Create a frame inside of the footer that will hold all of the controls
        row_controls = tk.Frame(footer)
        row_controls.grid(row=0, column=0, sticky='NSEW')

        # Add a create row button
        plus_image = gui.RenderImage('Assets\\plus.png', downscale=9)
        self.plus_button = ttk.Button(row_controls, takefocus=0, image=plus_image, state='disabled')
        self.plus_button['command'] = self.plus_row
        self.plus_button.image = plus_image
        self.plus_button.grid(row=0, column=0, padx=2, sticky='NSEW')

        # Add a delete row button
        minus_image = gui.RenderImage('Assets\\minus.png', downscale=9)
        self.minus_button = ttk.Button(row_controls, takefocus=0, image=minus_image, state='disabled')
        self.minus_button['command'] = self.minus_row
        self.minus_button.image = minus_image
        self.minus_button.grid(row=0, column=1, padx=2, sticky='NSEW')

        # Add a plot button
        plot_image = gui.RenderImage('Assets\\plot.png', downscale=9)
        self.plot_button = ttk.Button(footer, takefocus=0, image=plot_image, state='disabled')
        self.plot_button['command'] = self.open_flipbook
        self.plot_button.image = plot_image
        self.plot_button.grid(row=0, column=2, padx=2, sticky='NSEW')

        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(menu_bar, tearoff=0)
        self.file_menu.add_command(label='Load Files', command=self.listbox.Browse)
        self.file_menu.add_command(label='Add File', command=self.add_file)
        add_special = tk.Menu(menu_bar, tearoff=0)
        add_special.add_command(label='Peak Valley', command=lambda: self.add_file('Peak Valley'))
        self.file_menu.add_cascade(label='Add Special', menu=add_special)
        self.file_menu.add_command(label='Remove File', state='disabled', command=self.remove_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Save Preset', state='disabled', command=self.save_preset)
        self.file_menu.add_command(label='Load Preset', command=self.load_preset)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=lambda: self.root.destroy())
        menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.edit_menu = tk.Menu(menu_bar, tearoff=0)
        self.edit_menu.add_command(label='Clear Form', state='disabled', command=self.clear_all)
        self.edit_menu.add_command(label='Reset Form', state='disabled', command=self.reset)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Paste (Selected File)', state='disabled', command=self.paste_file)
        self.edit_menu.add_command(label='Paste (All Files)', state='disabled', command=self.paste_all)
        menu_bar.add_cascade(label='Edit', menu=self.edit_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label='View Help', command=self.open_help)
        help_menu.add_separator()
        help_menu.add_command(label='About', state='disabled')
        menu_bar.add_cascade(label='Help', menu=help_menu)
        self.root.config(menu=menu_bar)

        # Create keyboard shortcut that will function the same as clicking the 'Plot' button
        self.root.bind('<Return>', self.open_flipbook)

        # Create keyboard shortcuts for creating and deleting rows
        self.root.bind('<Control-minus>', self.minus_row)
        self.root.bind('<Control-=>', self.plus_row)

        # Create keyboard shortcuts for moving between notebook tabs
        self.root.bind('<Insert>',
            lambda event, direction='previous': self.switch_tab(event, direction)) # Insert
        self.root.bind('<Prior>',
            lambda event, direction='next': self.switch_tab(event, direction)) # Page Up

        # Create keyboard shortcuts for moving between rows of a notebook tab
        self.root.bind('<Control-Tab>',
            lambda event, direction='next': self.switch_row(event, direction))
        self.root.bind('<Control-Shift-Tab>',
            lambda event, direction='previous': self.switch_row(event, direction))

        self.clipboard = {
            'title': None,
            'x column': None,
            'y1 columns': None,
            'y2 columns': None,
            'x label': None,
            'y1 label': None,
            'y2 label': None,
        } # When copy and pasting on the GUI, the values are stored here

        self.plot_colors = {
                'blue':     'b',
                'green':    'g',
                'red':      'r',
                'cyan':     'c',
                'magenta':  'm',
                'yellow':   'y',
                'white':    'w',
                'black':    'k',
                'gray':     '#808080',
                'pink':     '#ff4d4d',
                'purple':   '#660066',
                'gold':     '#b38600',
                'orange':   '#ff6600',
                'brown':    '#663300',
                'lime':     '#00ff00',
            } # A list of all preset color options for plotting purposes


    def save_preset(self):
        """Copies all user inputs to a config file and saves in the specified location."""

        # Show a dialog box where the user can choose where to save the preset file
        valid = (('Configuration Files (*.ini)', '*.ini'),('All Files',"*.*"))
        location = fd.asksaveasfilename(title='Choose where to save the preset file',
                                        defaultextension='.ini',
                                        filetypes=valid)

        # Create a ConfigObj object, targeted at the specified filepath
        preset = configobj.ConfigObj(location)

        # Iterator through the file objects
        for f, file in enumerate(self.files):
            # For each plot in each file, filepath, data start row, label row, and unit row
            # will be the same. Record these under the main section for this file.
            preset[f'File {f+1}'] = {
                'filepath': self.inputs[f],
                'data start': file.data_row_entry.get(),
                'label row': file.label_row_entry.get(),
                'unit row': file.unit_row_entry.get() if file.unit_row_entry.get() else '',
            }

            # The rest of the inputs are specific to each plot. Iterate through each plot,
            # recording each one's inputs under a different subsection of the preset.
            for n in range(len(file.plots)):
                preset[f'File {f+1}'][f'Plot {n+1}'] = {
                    'title': self.files[f]._titles[n].get(),
                    'x column': self.files[f]._x_columns[n].get(),
                    'y1 columns': self.files[f]._y1_columns[n].get(),
                    'y2 columns': self.files[f]._y2_columns[n].get(),
                    'x label': self.files[f]._x_labels[n].get(),
                    'y1 label': self.files[f]._y1_labels[n].get(),
                    'y2 label': self.files[f]._y2_labels[n].get(),
                }

        # Save the completed preset file to the specified filepath
        preset.write()


    def load_preset(self, location=None):
        """Gets user input information from the specified preset file and pastes them
        into the GUI."""

        # If no location was specified, have the user navigate to the preset file
        if not location:
            location = fd.askopenfilename(title='Choose the preset file')

        # Initialize a ConfigObj object
        preset = configobj.ConfigObj(location)

        # If the user presses cancel or if the preset file is empty (possibly corrupt),
        # display a message and exit the function.
        if len(preset) == 0:
            message = 'It looks like the preset file you chose is either empty or not ' \
                      'formatted correctly. Please double check the file and try again.'
            mb.showinfo('Oops!', message)
            return

        # Grab the filepath for each file in the preset
        self.inputs = [info['filepath'] for file, info in preset.items()]

        # Insert the filepaths into the listbox
        self.listbox.clear()
        self.listbox.field['state'] = 'normal'
        for filepath in self.inputs: self.listbox.field.insert('end', ' ' + filepath)
        self.listbox.field['state'] = 'disable'
        self.listbox.field['justify'] = 'left'

        # With the inputs variable initialized, it is safe to enable all fields and
        # create tabs/rows for each input
        self.enable()
        self.input_controls()

        # Iterate through the preset and create the necessary number of rows for each file
        for f, (_, info) in enumerate(preset.items()):
            # If info has a length of greater than five, that means that rows need to be added.
            # The first five entries are filepath, data start row, label row, unit row, and
            # the first row that is already created by default for each file.
            if len(info) > 5:
                rows_needed = len(info) - 5
                for _ in range(rows_needed): self.plus_row(tab=f)

        # Iterate through the preset again and fill the GUI fields with the relevant data
        for f, (_, info) in enumerate(preset.items()):
            self.files[f].data_row_entry.insert(0, info['data start'])
            self.files[f].label_row_entry.insert(0, info['label row'])
            self.files[f].unit_row_entry.insert(0, info['unit row'])
            plots = [key for key in info.keys()
                     if key not in ['filepath', 'data start', 'label row', 'unit row']]
            for p, plot in enumerate(plots):
                self.files[f]._titles[p].insert(0, info[plot]['title'])
                self.files[f]._x_columns[p].insert(0, info[plot]['x column'])
                self.files[f]._y1_columns[p].insert(0, info[plot]['y1 columns'])
                self.files[f]._y2_columns[p].insert(0, info[plot]['y2 columns'])
                self.files[f]._x_labels[p].insert(0, info[plot]['x label'])
                self.files[f]._y1_labels[p].insert(0, info[plot]['y1 label'])
                self.files[f]._y2_labels[p].insert(0, info[plot]['y2 label'])


    def browse(self):
        """Allow the user to browse for inputs, then initialize the GUI."""

        # Only run this code if there are inputs stored in the listbox
        if self.listbox.get():
            self.inputs = self.listbox.get()
            self.enable()
            self.input_controls()


    def enable(self):
        """Change the GUI to its enabled state, which only occurs when inputs are loaded."""

        # Enable the buttons in the footer
        self.plot_button['state'] = 'normal'
        self.plus_button['state'] = 'normal'
        self.minus_button['state'] = 'normal'

        # Enable the entries in the file menu
        # self.file_menu.entryconfig(1, state='normal')
        self.file_menu.entryconfig(3, state='normal')
        self.file_menu.entryconfig(5, state='normal')
        # self.file_menu.entryconfig(2, state='normal')
        # self.file_menu.entryconfig(4, state='normal')

        # Enable the entries in the edit menu
        self.edit_menu.entryconfig(0, state='normal')
        self.edit_menu.entryconfig(1, state='normal')
        self.edit_menu.entryconfig(3, state='normal')
        self.edit_menu.entryconfig(4, state='normal')


    def reset(self):
        """Revert the GUI back to its disabled state, before any inputs were loaded."""

        # Clear the listbox
        self.listbox.clear()

        # Disable the buttons in the footer
        self.plot_button['state'] = 'disabled'
        self.plus_button['state'] = 'disabled'
        self.minus_button['state'] = 'disabled'

        # Disable the entries in the file menu
        # self.file_menu.entryconfig(1, state='disabled')
        self.file_menu.entryconfig(3, state='disabled')
        self.file_menu.entryconfig(5, state='disabled')
        # self.file_menu.entryconfig(2, state='disabled')
        # self.file_menu.entryconfig(4, state='disabled')

        # Disable the entries in the edit menu
        self.edit_menu.entryconfig(0, state='disabled')
        self.edit_menu.entryconfig(1, state='disabled')
        self.edit_menu.entryconfig(3, state='disabled')
        self.edit_menu.entryconfig(4, state='disabled')

        # Destroy everything in the primary frame - namely, the notebook
        for child in self.primary.winfo_children(): child.destroy()

        # Recreate the message that lets the user know there are no inputs loaded
        message = 'Please provide at least one input file.\n\nControls will appear here.'
        no_input_label = tk.Label(self.primary, text=message)
        no_input_label.grid(row=0, column=0, sticky='NSEW')


    def input_controls(self, special=None):
        """Creates a tab for each input file, and one row for each tab."""

        # Destroy everything in the primary frame
        for child in self.primary.winfo_children(): child.destroy()

        # Place a notebook in the primary frame
        self.notebook = ttk.Notebook(self.primary, takefocus=0)
        self.notebook.grid(row=0, column=0, sticky='NSEW')

        # Create an object file for each input and add them to a list to keep track
        if not special:
            self.files = [BasicFile(self.notebook, filepath) for filepath in self.inputs]
        elif special == 'Peak Valley':
            self.files = [PeakValleyFile(self.notebook, filepath) for filepath in self.inputs]

        # Set cursor focus on the default field of the first tab for ease of use
        self.files[0].set_default_focus()


    def plus_row(self, event=None, tab=None):
        """Add a row to the specified file/tab of the notebook."""

        try:
            # If a tab is not specified, set tab equal to the index of the current tab.
            # This is the case when clicking the 'create row' button on the GUI.
            # Otherwise, the tab parameter is used when loading presets, etc.
            if not tab: tab = self.notebook.index(self.notebook.select())
            # Add a row to the tab
            self.files[tab].add_row()
        except NameError: pass


    def minus_row(self, event=None, tab=None):
        """Remove a row from the specified file/tab of the notebook."""

        try:
            # If a tab is not specified, set tab equal to the index of the current tab.
            # This is the case when clicking the 'delete row' button on the GUI.
            # Otherwise, the tab parameter is used when loading presets, etc.
            if not tab: tab = self.notebook.index(self.notebook.select())
            # Remove a row from the tab
            self.files[tab].delete_row()
        except NameError: pass


    def add_file(self, special=None):
        """Retroactively add a file to the current inputs."""

        # Ask the user to locate the file he/she wishes to add
        filepath = fd.askopenfilename(title='Choose the file')

        # Don't continue if no filepath was selected by the user
        if len(filepath) == 0: return

        # Append the filepath to the list of inputs
        self.inputs.append(filepath)

        if len(self.inputs) == 1:
            # A length of one of the inputs list implies that the user is trying
            # to add a file to a freshly resetted program; handle differely
            self.enable()
            self.input_controls(special)
            self.listbox.clear()
        else:
            # Create a basic file object by default
            if not special:
                file = BasicFile(self.notebook, filepath)
            # Otherwise, if the user is adding a special file, create the
            # appropriate file object
            elif special == 'Peak Valley':
                file = PeakValleyFile(self.notebook, filepath)
            # Append it to the list of file objects
            self.files.append(file)

        # Add the filepath to the listbox
        self.listbox.field['state'] = 'normal'
        self.listbox.field.insert('end', filepath)
        self.listbox.field['state'] = 'disable'
        self.listbox.field['justify'] = 'left'

        # Select the newly added notebook tab
        self.notebook.select(len(self.files)-1)


    def remove_file(self):
        """Retroactively remove a file from the current inputs."""

        # Don't continue if the currently selected file is the last remaining input
        if not len(self.files) > 1: return

        # Get the index of the currently selected tab
        current = self.notebook.index(self.notebook.select())

        # Delete the information about this tab that is stored in the inputs and files lists
        del(self.inputs[current])
        del(self.files[current])

        # Destroy the currently selected tab
        # The select method of a notebook gives a name; however, the nametowidget method
        # finds the respective object
        app.root.nametowidget(self.notebook.select()).destroy()

        # Remove the filepath from the listbox
        self.listbox.field['state'] = 'normal'
        self.listbox.field.delete(current)
        self.listbox.field['state'] = 'disable'
        self.listbox.field['justify'] = 'left'


    def switch_tab(self, event, direction):
        """Switch to either the next or previous tab in the notebook."""

        # Get the index of the tab that the user wants to go to
        current = self.notebook.index(self.notebook.select())
        destination = (current + 1) if direction == 'next' else (current - 1)
        try:
            # Attempt to select the notebook tab
            self.notebook.select(destination)
        except (NameError, tk.TclError):
            pass # If the currently selected tab is either the first or the last, do nothing
        else:
            # If there was no error, set cursor focus on the data start row entry
            self.files[destination].set_default_focus()


    def switch_row(self, event, direction):
        """Switch to the same field that is currently selected in either the next
        or previous row."""

        # Get a reference to the File object that is currently selected
        current = self.notebook.index(self.notebook.select())
        file = self.files[current]

        # Create a list that contains all possible fields contained in each row
        fields = [file._titles, file._x_columns, file._y1_columns, file._y2_columns,
                  file._x_labels, file._y1_labels, file._y2_labels]

        # Iterate through the list and find the widget that currently has focus,
        # then store which entry it is as well as the row that it's in
        for f, field in enumerate(fields):
            for i, item in enumerate(field):
                if item == app.root.focus_get():
                    entry = f
                    row = i
                    break # Once the field is found, break from the loop
            else:
                continue # Continue if the inner loop was not broken
            break # If the inner loop was broken, break from the outer loop
        else:
            # If the widget was not found, don't execute any of the following code.
            # This is intended to happen with the data start, label, and unit row entries.
            return

        # Get the index of the row that the user wants to go to
        destination = (row + 1) if direction == 'next' else (row - 1)

        # If the row exists, find the relevant widget and set focus on it
        if destination in range(len(fields[entry])):
            next_widget = fields[entry][destination]
            next_widget.focus_set()

        # Return 'break' to bypass event propagation
        return ('break')


    def open_flipbook(self, event=None):
        """Open the flipbook."""

        # If the flipbook is already open, exit the function
        if self.FLIPBOOK: return

        # Store all of the inputs in each tab
        for file in self.files: file.generate()

        # Hide the main window and open the flipbook object
        app.root.withdraw()
        Flipbook(app.root, info=self.files)
        self.FLIPBOOK = True


    def open_help(self, event=None):
        """Open the help window."""

        # If the help window is already open, exit the function
        if self.HELP: return

        # Open the help window
        help_window = Help(app.root)
        self.HELP = True


    def paste_file(self):
        """Paste the contents of the clipboard into every row of the currently
        selected file."""

        # Get the index of the currently selected notebook tab
        current = self.notebook.index(self.notebook.select())

        # Iterate through the rows of the currently selected file and delete the
        # contents of every field, then insert the contents of the clipboard.
        for row in range(len(self.files[current]._rows)):
            if self.clipboard['title']:
                self.files[current]._titles[row].delete(0, 'end')
                self.files[current]._titles[row].insert(0, self.clipboard['title'])
            if self.clipboard['x column']:
                self.files[current]._x_columns[row].delete(0, 'end')
                self.files[current]._x_columns[row].insert(0, self.clipboard['x column'])
            if self.clipboard['y1 columns']:
                self.files[current]._y1_columns[row].delete(0, 'end')
                self.files[current]._y1_columns[row].insert(0, self.clipboard['y1 columns'])
            if self.clipboard['y2 columns']:
                self.files[current]._y2_columns[row].delete(0, 'end')
                self.files[current]._y2_columns[row].insert(0, self.clipboard['y2 columns'])
            if self.clipboard['x label']:
                self.files[current]._x_labels[row].delete(0, 'end')
                self.files[current]._x_labels[row].insert(0, self.clipboard['x label'])
            if self.clipboard['y1 label']:
                self.files[current]._y1_labels[row].delete(0, 'end')
                self.files[current]._y1_labels[row].insert(0, self.clipboard['y1 label'])
            if self.clipboard['y2 label']:
                self.files[current]._y2_labels[row].delete(0, 'end')
                self.files[current]._y2_labels[row].insert(0, self.clipboard['y2 label'])


    def paste_all(self):
        """Paste the contents of the clipboard into every row of every file."""

        # Iterate through the rows of each file and delete the contents of
        # every field, then insert the contents of the clipboard.
        for file in self.files:
            for row in range(len(file._rows)):
                if self.clipboard['title']:
                    file._titles[row].delete(0, 'end')
                    file._titles[row].insert(0, self.clipboard['title'])
                if self.clipboard['x column']:
                    file._x_columns[row].delete(0, 'end')
                    file._x_columns[row].insert(0, self.clipboard['x column'])
                if self.clipboard['y1 columns']:
                    file._y1_columns[row].delete(0, 'end')
                    file._y1_columns[row].insert(0, self.clipboard['y1 columns'])
                if self.clipboard['y2 columns']:
                    file._y2_columns[row].delete(0, 'end')
                    file._y2_columns[row].insert(0, self.clipboard['y2 columns'])
                if self.clipboard['x label']:
                    file._x_labels[row].delete(0, 'end')
                    file._x_labels[row].insert(0, self.clipboard['x label'])
                if self.clipboard['y1 label']:
                    file._y1_labels[row].delete(0, 'end')
                    file._y1_labels[row].insert(0, self.clipboard['y1 label'])
                if self.clipboard['y2 label']:
                    file._y2_labels[row].delete(0, 'end')
                    file._y2_labels[row].insert(0, self.clipboard['y2 label'])


    def clear_all(self):
        """Clears the contents of every field."""

        # Iterate through each file, deleting the contents of each field.
        for file in self.files:
            file.data_row_entry.delete(0, 'end')
            file.label_row_entry.delete(0, 'end')
            file.unit_row_entry.delete(0, 'end')
            for row in range(len(file._rows)):
                file._titles[row].delete(0, 'end')
                file._x_columns[row].delete(0, 'end')
                file._y1_columns[row].delete(0, 'end')
                file._y2_columns[row].delete(0, 'end')
                file._x_labels[row].delete(0, 'end')
                file._y1_labels[row].delete(0, 'end')
                file._y2_labels[row].delete(0, 'end')


    def test(self):
        """Function that loads a preset and opens the flipbook for testing purposes."""

        self.load_preset('Presets\\preset.ini')
        # self.load_preset('Presets\\laptop.ini')
        self.open_flipbook()


class BasicFile(gui.ScrollableTab):
    """A scrollable notebook tab that supports dynamically creating and deleting basic
    rows (plots), and stores all of the user-specified information about each plot."""

    def __init__(self, notebook, filepath):
        """Initialize the scrollable notebook tab as well as the lists that will hold
        references to each field in each row. Creates the data start row, label row,
        and unit row entry fields for the file and adds a single row by default."""

        self.filepath = filepath
        self.filename = self.filepath.split('/')[-1]
        gui.ScrollableTab.__init__(self, notebook, self.filename, cwidth=571, cheight=252)

        # Initialize internal variables and field-reference storage lists
        self._count = 0
        self._rows = []
        self._titles = []
        self._x_columns = []
        self._y1_columns = []
        self._y2_columns = []
        self._x_labels = []
        self._y1_labels = []
        self._y2_labels = []

        # Hold a reference to each row/plot in order to be used outside of the class
        self.plots = []

        # Create a frame to hold the general file settings/controls
        controls = tk.Frame(self)
        controls.grid(row=0, column=0, pady=20, sticky='NSEW')
        for column in [0, 3, 6, 9]:
            controls.columnconfigure(column, weight=1)

        # Create label and entry fields where the user can enter the data start row
        data_row_label = tk.Label(controls, text='Data start row:')
        data_row_label.grid(row=0, column=1, sticky='NSEW')

        self.data_row_entry = ttk.Entry(controls, width=10)
        self.data_row_entry.grid(row=0, column=2, padx=5, sticky='NSEW')

        # Create label and entry fields where the user can enter the label row
        label_row_label = tk.Label(controls, text='Label row:')
        label_row_label.grid(row=0, column=4, sticky='NSEW')

        self.label_row_entry = ttk.Entry(controls, width=10)
        self.label_row_entry.grid(row=0, column=5, padx=5, sticky='NSEW')

        # Create label and entry fields where the user can enter the unit row
        unit_row_label = tk.Label(controls, text='Unit row:')
        unit_row_label.grid(row=0, column=7, sticky='NSEW')

        self.unit_row_entry = ttk.Entry(controls, width=10)
        self.unit_row_entry.grid(row=0, column=8, padx=5, sticky='NSEW')

        # Make each field scroll into view upon a focus event
        self.data_row_entry.bind('<FocusIn>', self._scroll_into_view)
        self.label_row_entry.bind('<FocusIn>', self._scroll_into_view)
        self.unit_row_entry.bind('<FocusIn>', self._scroll_into_view)

        # Add a row/plot by default
        self.add_row()

    def add_row(self):
        """Add a row/plot to the current file."""

        # Define padding constants
        MARGIN = 8
        TOOLS = 2
        PADDING = 5

        # Create a label frame that will hold the contents of each row
        frame = tk.LabelFrame(self, text=f'Plot {self._count + 1}')
        frame.grid(row=self._count + 1, column=0, padx=MARGIN, pady=(0, MARGIN*2), sticky='NSEW')
        frame.columnconfigure(0, weight=1)

        # Create a frame that everything else will be placed inside of
        inner = tk.Frame(frame)
        inner.grid(row=0, column=0, padx=MARGIN*2, pady=MARGIN*2, sticky='NSEW')
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(2, weight=1)
        inner.columnconfigure(3, weight=10)

        # Create a frame that will hold all of the tools for the row
        tools = tk.Frame(inner)
        tools.grid(row=0, column=0, columnspan=4, padx=PADDING, sticky='NSEW')
        tools.columnconfigure(1, weight=1)

        # Create label and entry fields where the user can enter the title
        title_label = tk.Label(tools, text='Title:')
        title_label.grid(row=0, column=0, sticky='NSEW')

        title_entry = ttk.Entry(tools)
        title_entry.grid(row=0, column=1, padx=PADDING, sticky='NSEW')
        self._titles.append(title_entry)

        # Create a copy button
        copy_image = gui.RenderImage('Assets\\copy.png', downscale=12)
        copy_button = ttk.Button(tools, takefocus=0, width=3, image=copy_image, text='C')
        copy_button['command'] = lambda ID=self._count: self.copy(ID)
        copy_button.image = copy_image
        copy_button.grid(row=0, column=2, padx=TOOLS, sticky='NSEW')

        # Create a paste button
        paste_image = gui.RenderImage('Assets\\paste.png', downscale=12)
        paste_button = ttk.Button(tools, takefocus=0, width=3, image=paste_image, text='P')
        paste_button['command'] = lambda ID=self._count: self.paste(ID)
        paste_button.image = paste_image
        paste_button.grid(row=0, column=3, padx=TOOLS, sticky='NSEW')

        # Create a clear button
        clear_image = gui.RenderImage('Assets\\clear.png', downscale=12)
        clear_button = ttk.Button(tools, takefocus=0, width=3, image=clear_image, text='X')
        clear_button['command'] = lambda ID=self._count: self.clear(ID)
        clear_button.image = clear_image
        clear_button.grid(row=0, column=4, padx=TOOLS, sticky='NSEW')

        # Add spacing between the tools and the next row of fields
        gui.Space(inner, row=1, column=0, columnspan=4, padding=PADDING)

        # Create label and entry fields where the user can enter the x-axis columns
        x_column_label = tk.Label(inner, text='x column:')
        x_column_label.grid(row=2, column=0, padx=PADDING, sticky='NSEW')

        x_column_entry = ttk.Entry(inner, width=10)
        x_column_entry.grid(row=3, column=0, padx=PADDING, sticky='NSEW')
        self._x_columns.append(x_column_entry)

        # Create label and entry fields where the user can enter the primary axis columns
        y1_column_label = tk.Label(inner, text='y1 columns:')
        y1_column_label.grid(row=2, column=1, padx=PADDING, sticky='NSEW')

        y1_column_entry = ttk.Entry(inner, width=10)
        y1_column_entry.grid(row=3, column=1, padx=PADDING, sticky='NSEW')
        self._y1_columns.append(y1_column_entry)

        # Create label and entry fields where the user can enter the secondary axis columns
        y2_column_label = tk.Label(inner, text='y2 columns:')
        y2_column_label.grid(row=2, column=2, padx=PADDING, sticky='NSEW')

        y2_column_entry = ttk.Entry(inner, width=10)
        y2_column_entry.grid(row=3, column=2, padx=PADDING, sticky='NSEW')
        self._y2_columns.append(y2_column_entry)

        # Create label and entry fields where the user can enter the x-axis label
        x_axis_label = tk.Label(inner, text='x axis label:')
        x_axis_label.grid(row=2, column=3, padx=PADDING, sticky='NSEW')

        x_axis_entry = ttk.Entry(inner)
        x_axis_entry.grid(row=3, column=3, padx=PADDING, sticky='NSEW')
        self._x_labels.append(x_axis_entry)

        # Add spacing between the first and second rows of fields
        gui.Space(inner, row=4, column=0, columnspan=4, padding=PADDING)

        # Create label and entry fields where the user can enter the primary axis label
        y1_axis_label = tk.Label(inner, text='y1 axis label:')
        y1_axis_label.grid(row=5, column=0, columnspan=3, padx=PADDING, sticky='NSEW')

        y1_axis_entry = ttk.Entry(inner)
        y1_axis_entry.grid(row=6, column=0, columnspan=3, padx=PADDING, sticky='NSEW')
        self._y1_labels.append(y1_axis_entry)

        # Create label and entry fields where the user can enter the secondary axis label
        y2_axis_label = tk.Label(inner, text='y2 axis label:')
        y2_axis_label.grid(row=5, column=3, padx=PADDING, sticky='NSEW')

        y2_axis_entry = ttk.Entry(inner)
        y2_axis_entry.grid(row=6, column=3, padx=PADDING, sticky='NSEW')
        self._y2_labels.append(y2_axis_entry)

        # Make each field scroll into view upon a focus event
        title_entry.bind('<FocusIn>', self._scroll_into_view)
        x_column_entry.bind('<FocusIn>', self._scroll_into_view)
        y1_column_entry.bind('<FocusIn>', self._scroll_into_view)
        y2_column_entry.bind('<FocusIn>', self._scroll_into_view)
        x_axis_entry.bind('<FocusIn>', self._scroll_into_view)
        y1_axis_entry.bind('<FocusIn>', self._scroll_into_view)
        y2_axis_entry.bind('<FocusIn>', self._scroll_into_view)

        # Increment the row count, keep a reference to the frame, and create a plot object
        self._count += 1
        self._rows.append(frame)
        self.add_plot()

    def delete_row(self):
        """Delete a row/plot from the bottom of the current file."""

        # Only allow a row/plot to be deleted if there is more than one row/plot
        if len(self._rows) <= 1: return

        # Destroy the last row, removing it from the GUI
        self._rows[-1].destroy()
        # Delete references to the deleted row/plot
        del(self._rows[-1])
        del(self.plots[-1])
        # Decrement the row/plot count
        self._count -= 1

    def _scroll_into_view(self, event):
        """Scrolls the bound widget into view instead of only moving focus offscreen."""

        # Get the current coordinates of the tops and bottoms of the widget and canvas
        widget_top = event.widget.winfo_rooty()
        widget_bottom = widget_top + event.widget.winfo_height()
        canvas_top = self.canvas.winfo_rooty()
        canvas_bottom = canvas_top + self.canvas.winfo_height()

        # Get the parent and grandparent of the widget
        parent_inner = app.root.nametowidget(event.widget.winfo_parent())
        parent_outer = app.root.nametowidget(parent_inner.winfo_parent())

        # Define a certain amount of padding to act as a buffer
        BUFFER = 30
        if widget_bottom > canvas_bottom:
            delta = int(widget_bottom - canvas_bottom) + BUFFER
            self.canvas.yview_scroll(delta, 'units')
        elif widget_top < canvas_top:
            delta = int(widget_top - canvas_top) - BUFFER
            self.canvas.yview_scroll(delta, 'units')

    def set_default_focus(self):
        self.data_row_entry.focus_set()

    def copy(self, ID):
        """Copies the contents of the selected row to the clipboard."""

        app.clipboard['title'] = self._titles[ID].get()
        app.clipboard['x column'] = self._x_columns[ID].get()
        app.clipboard['y1 columns'] = self._y1_columns[ID].get()
        app.clipboard['y2 columns'] = self._y2_columns[ID].get()
        app.clipboard['x label'] = self._x_labels[ID].get()
        app.clipboard['y1 label'] = self._y1_labels[ID].get()
        app.clipboard['y2 label'] = self._y2_labels[ID].get()

    def paste(self, ID):
        """Pastest the contents of the clipboards into the selected row."""

        self.clear(ID)
        self._titles[ID].insert(0, app.clipboard['title'])
        self._x_columns[ID].insert(0, app.clipboard['x column'])
        self._y1_columns[ID].insert(0, app.clipboard['y1 columns'])
        self._y2_columns[ID].insert(0, app.clipboard['y2 columns'])
        self._x_labels[ID].insert(0, app.clipboard['x label'])
        self._y1_labels[ID].insert(0, app.clipboard['y1 label'])
        self._y2_labels[ID].insert(0, app.clipboard['y2 label'])

    def clear(self, ID):
        """Clears the contents of the selected row."""

        self._titles[ID].delete(0, 'end')
        self._x_columns[ID].delete(0, 'end')
        self._y1_columns[ID].delete(0, 'end')
        self._y2_columns[ID].delete(0, 'end')
        self._x_labels[ID].delete(0, 'end')
        self._y1_labels[ID].delete(0, 'end')
        self._y2_labels[ID].delete(0, 'end')

    def add_plot(self):
        """Create a new plot object and hold a reference to it."""

        class Plot:
            """Object that holds information about a singular plot."""

            def __init__(self):
                """Initialize the object's attributes."""

                # Keep track of the columns to plot and the title/axis labels
                self.x = None
                self.y1 = None
                self.y2 = None
                self.title = None
                self.x_label = None
                self.y1_label = None
                self.y2_label = None

                # Keep track of whether or not a secondary axis is required
                self.secondary_axis = None

                # Keep track of original axis limits
                self.x_lower_original = None
                self.x_upper_original = None
                self.y1_lower_original = None
                self.y1_upper_original = None
                self.y2_lower_original = None
                self.y2_upper_original = None

                # Keep track of axis limits
                self.x_lower = None
                self.x_upper = None
                self.y1_lower = None
                self.y1_upper = None
                self.y2_lower = None
                self.y2_upper = None

                # Keep track of number of primary and secondary ticks
                self.primary_ticks = None
                self.secondary_ticks = None

                # Keep track of the style selection
                self.style = tk.StringVar()
                self.style.set('Default')

                # Keep track of the background selection, and path if necessary
                self.background = tk.StringVar()
                self.background.set('None')
                self.background_path = None

                # Keep tracks of tolerance band information
                self.bands = ToleranceBands()
                self.series = []
                self.color = []
                self.linestyle = []
                self.minus_tolerance = []
                self.plus_tolerance = []
                self.lag = []
                self.plus_bands = []
                self.minus_bands = []

                # Keep track of limit line information
                self.lines = LimitLines()
                self.line_axis = []
                self.line_orientation = []
                self.line_value = []
                self.line_color = []
                self.line_style = []
                self.line_alpha = []

            def _x_data(self, x_column):
                """Pull the appropriate x-information from the data."""

                return self.data[self.labels[x_column-1]]

            def _y_data(self, y_columns):
                """Pull the appropriate y-information from the data."""

                return [self.data[self.labels[column-1]] for column in y_columns]

            def _generate(self, data, labels, x_column, y1_columns, y2_columns=None,
                          units=None):
                """The main function for the object which stores the inputs and calls
                other relevant functions."""

                # Store the inputs as instance variables
                self.data = data
                self.labels = labels
                self.units = units
                self.x_column = x_column
                self.y1_columns = y1_columns
                self.y2_columns = y2_columns

                # Grab the relevant data and store as instance variables
                self.x = self._x_data(x_column)
                self.y1 = self._y_data(y1_columns)
                self.y2 = self._y_data(y2_columns) if y2_columns else None

            def _labels(self, title, x_label, y1_label, y2_label):
                """Store the label inputs as instance variables. This is separate from
                the _generate method solely because it didn't feel like it fit there."""

                # Store the label inputs as instance variables
                self.title = title if title else None
                self.x_label = x_label if x_label else None
                self.y1_label = y1_label if y1_label else None
                self.y2_label = y2_label if y2_label else None

            def update_plot(self, flipbook, file, number):
                # ========================
                # STYLE SELECTION CONTROLS
                # ========================

                # Set the style according to whatever the user has selected
                # Must come before the main section or else things like the legend won't update
                if self.style.get() == 'Default':
                    plt.style.use('default')
                elif self.style.get() == 'Classic':
                    plt.style.use('classic')
                elif self.style.get() == 'Seaborn':
                    plt.style.use('seaborn')
                elif self.style.get() == 'Fivethirtyeight':
                    plt.style.use('fivethirtyeight')

                # =================
                # MAIN UPDATE LOGIC
                # =================

                # Display the filename of the current plot
                flipbook.filename.set(f'{flipbook.info[file].filename} - Plot {number + 1}')

                # Essentially reset the secondary axis by clearing and turning it off if it exists,
                # then setting the self.secondary variable to None
                if flipbook.secondary:
                    flipbook.secondary.clear()
                    flipbook.secondary.axis('off')
                flipbook.secondary = None

                # Create a variable that keeps track of if a secondary axis is necessary
                self.secondary_axis = True if self.y2 else False
                # If it is, create the secondary axis
                if self.secondary_axis: flipbook.secondary = flipbook.primary.twinx()

                # Clear the primary axis as well
                flipbook.primary.clear()

                # Set the appropriate coordinates format to display on the flipbook
                if self.secondary_axis:
                    flipbook.primary.set_zorder(1)
                    flipbook.secondary.set_zorder(100)
                    flipbook.secondary.format_coord = flipbook._coordinates(flipbook.secondary, flipbook.primary,
                                                                    self.secondary_axis)
                if not self.secondary_axis:
                    flipbook.primary.set_zorder(1000)
                    flipbook.primary.format_coord = flipbook._coordinates(flipbook.primary, None, self.secondary_axis)

                # Choose colors for the primary axis - will be iterated-through sequentially
                y1_colors = ['k', 'b', 'r', 'g', app.plot_colors['purple'], app.plot_colors['orange'],
                            app.plot_colors['brown']]
                # Create a copy of the primary axis plot colors
                y1_plot_colors = y1_colors[:]
                # Choose colors for the secondary axis - will be iterated-through sequentially
                y2_colors = [app.plot_colors['gray'], 'c', app.plot_colors['pink'], app.plot_colors['lime'],
                            'm', app.plot_colors['gold'], 'y']
                # Create a copy of the secondary axis plot colors
                y2_plot_colors = y2_colors[:]

                # Keep track of each handle, label, and how many times the colors are repeated
                handles = []
                labels = []
                repeated = 0
                # Iterate through the primary axis data for the current plot
                for y, y1 in enumerate(self.y1):
                    # Determine how many times the colors list will be repeated
                    if y % len(y1_plot_colors) == 0: repeated += 1
                    # Determine the color of the line
                    color = y1_plot_colors[y - repeated * len(y1_plot_colors)]
                    # Get the column label and plot the line
                    column = self.y1_columns[y]
                    label = self.labels[column-1]
                    line = flipbook.primary.plot(self.x, y1, color, label=label)
                    handles.append(line[0])
                    labels.append(label)
                # If there is data to be plotted on the secondary axis, run the following code
                if self.secondary_axis:
                    repeated = 0
                    # Iterate through the secondary axis data for the current plot
                    for y, y2 in enumerate(self.y2):
                        # Determine how many times the colors list will be repeated
                        if y % len(y2_plot_colors) == 0: repeated += 1
                        # Determine the colors of the line
                        color = y2_plot_colors[y - repeated * len(y2_plot_colors)]
                        # Get the column label and plot the line
                        column = self.y2_columns[y]
                        label = self.labels[column-1]
                        line = flipbook.secondary.plot(self.x, y2, color, label=label)
                        handles.append(line[0])
                        labels.append(label)

                # Determine adequate padding for the x-axis and set the x-axis limits accordingly.
                # Store the original x-axis limits to allow the user to revert to them if desired.
                min_x = min(self.x.dropna())
                max_x = max(self.x.dropna())
                padding = (max_x - min_x) * (100/90) * (0.05)
                self.x_lower_original = min_x - padding
                self.x_upper_original = max_x + padding
                flipbook.primary.set_xlim(self.x_lower_original, self.x_upper_original)
                # Store the original y-axis limits to allow the user to revert to them if desired.
                self.y1_lower_original = flipbook.primary.get_ylim()[0]
                self.y1_upper_original = flipbook.primary.get_ylim()[1]
                if self.secondary_axis:
                    self.y2_lower_original = flipbook.secondary.get_ylim()[0]
                    self.y2_upper_original = flipbook.secondary.get_ylim()[1]

                # Turn the grid on, with both major and minor gridlines
                flipbook.primary.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)
                flipbook.primary.minorticks_on()
                flipbook.primary.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
                if self.secondary_axis:
                    flipbook.secondary.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)

                # Set the title, x axis label, and y axes labels according to user input
                flipbook.figure.suptitle(self.title, fontweight='bold', fontsize=14)
                # Set the axis labels
                flipbook.primary.set_xlabel(self.x_label)
                flipbook.primary.set_ylabel(self.y1_label)
                if self.secondary_axis: flipbook.secondary.set_ylabel(self.y2_label)
                # # Use the official representation of the object in case tex expressions are used
                # flipbook.primary.set_xlabel(repr(self.x_label)[1:-1])
                # flipbook.primary.set_ylabel(repr(self.y1_label)[1:-1])
                # if self.secondary_axis: flipbook.secondary.set_ylabel(repr(self.y2_label)[1:-1])

                # Determine the number of lines being plotted
                lines = len(flipbook.primary.lines)
                if self.secondary_axis: lines += len(flipbook.secondary.lines)
                # Specify the maximum number of columns per row in the legend, and calculate
                # the number of rows accordingly
                max_columns = 5
                rows = lines / max_columns
                # If there will be more than two rows, calculate the number of columns required
                # to keep the legend at two rows
                if rows > 2: max_columns = math.ceil(lines / 2)
                # Create the legend
                legend = flipbook.primary.legend(
                                handles = handles,
                                labels = labels,
                                loc = 'lower left',
                                fancybox = True,
                                shadow = True,
                                ncol = max_columns,
                                mode = 'expand',
                                bbox_to_anchor = (-0.15, -0.2, 1.265, 0.1),
                    )
                # Make the legend draggable (possibly a control in the future)
                legend.set_draggable(state=True)

                # Map the items in the legend to its corresponding line
                flipbook.line_map = {}
                for legend_line, original_line in zip(legend.get_lines(), handles):
                    legend_line.set_picker(5)
                    flipbook.line_map[legend_line] = original_line

                # # If the controls window has not been created yet, create it and leave it hidden
                # if not flipbook.controls:
                #     flipbook.controls = Controls(flipbook, flipbook.plots[flipbook.page])
                #     flipbook.controls.withdraw()

                # ====================
                # AXES LIMITS CONTROLS
                # ====================

                # Set each axis limit to the user-specified value
                if self.x_lower: flipbook.primary.set_xlim(left=self.x_lower)
                if self.x_upper: flipbook.primary.set_xlim(right=self.x_upper)
                if self.y1_lower: flipbook.primary.set_ylim(bottom=self.y1_lower)
                if self.y1_upper: flipbook.primary.set_ylim(top=self.y1_upper)
                if self.y2_lower: flipbook.secondary.set_ylim(bottom=self.y2_lower)
                if self.y2_upper: flipbook.secondary.set_ylim(top=self.y2_upper)

                # ===================
                # AXES TICKS CONTROLS
                # ===================

                # Set a standard number of axis ticks to make it easier to line up the gridlines
                if self.primary_ticks:
                    PRIMARY = flipbook.primary.get_ylim()
                    flipbook.primary.set_yticks(np.linspace(PRIMARY[0], PRIMARY[1],
                                            int(self.primary_ticks)))
                if self.secondary_ticks:
                    SECONDARY = flipbook.secondary.get_ylim()
                    flipbook.secondary.set_yticks(np.linspace(SECONDARY[0], SECONDARY[1],
                                            int(self.secondary_ticks)))

                # =============================
                # BACKGROUND SELECTION CONTROLS
                # =============================

                def set_background(choice):
                    """Set whatever image the user selected as the plot background."""

                    # If 'None' is selected, no background is drawn
                    if choice == 'None': return
                    # Otherwise, load a background preset
                    elif choice == 'Tactair': path = 'Assets\\tactair.bmp'
                    elif choice == 'Young & Franklin': path = 'Assets\\yf.bmp'
                    # 'Custom' loads the background from a preset file
                    elif choice == 'Custom': path = self.background_path
                    # Load the image and display it on the plot
                    image = plt.imread(gui.ResourcePath(path))
                    x_low, x_high = flipbook.primary.get_xlim()
                    y_low, y_high = flipbook.primary.get_ylim()
                    flipbook.primary.imshow(image, extent=[x_low, x_high, y_low, y_high], aspect='auto')

                # Set the background of the plot
                set_background(self.background.get())

                # =======================
                # TOLERANCE BAND CONTROLS
                # =======================

                # Iterate through the plus bands of the current plot
                for p, plus in enumerate(self.plus_bands):
                    # If there are no plus bands, skip to next iteration
                    if not plus: continue
                    # Plot the plus band on the appropriate axis
                    elif plus[0] == 'primary':
                        flipbook.primary.plot(self.x, plus[1], app.plot_colors[self.color[p]],
                                        linestyle=self.linestyle[p])
                    elif plus[0] == 'secondary':
                        flipbook.secondary.plot(self.x, plus[1], app.plot_colors[self.color[p]],
                                        linestyle=self.linestyle[p])
                # Iterate through the minus bands of the current plot
                for m, minus in enumerate(self.minus_bands):
                    # If there are no minus bands, skip to next iteration
                    if not minus: continue
                    # Plot the minus band on the appropriate axis
                    elif minus[0] == 'primary':
                        flipbook.primary.plot(self.x, minus[1], app.plot_colors[self.color[m]],
                                        linestyle=self.linestyle[m])
                    elif minus[0] == 'secondary':
                        flipbook.secondary.plot(self.x, minus[1], app.plot_colors[self.color[m]],
                                        linestyle=self.linestyle[m])

                # ===================
                # LIMIT LINE CONTROLS
                # ===================

                # Iterate through the values list of the limit lines
                for v, value in enumerate(self.line_value):
                    # If there are no values, skip to next iteration (e.g. blank rows)
                    if not value: continue
                    # Determine the axis to plot the limit line on
                    axis = flipbook.primary if self.line_axis[v] == 'primary' else \
                        ( flipbook.secondary if self.line_axis[v] == 'secondary' and \
                            self.secondary_axis else None )
                    # Plot the limit line after determining its orientation
                    if self.line_orientation[v] == 'vertical':
                        axis.axvline(x=float(self.line_value[v]),
                                    linestyle=self.line_style[v],
                                    color=app.plot_colors[self.line_color[v]],
                                    alpha=float(self.line_alpha[v]))
                    elif self.line_orientation[v] == 'horizontal':
                        axis.axhline(y=float(self.line_value[v]),
                                    linestyle=self.line_style[v],
                                    color=app.plot_colors[self.line_color[v]],
                                    alpha=float(self.line_alpha[v]))

        # Create a new plot object and hold a reference to it
        plot = Plot()
        self.plots.append(plot)

    def _filetype(self, path):
        """Determine the filetype of the input."""

        name, extension = os.path.splitext(path)
        if extension in ['.csv', '.dat']: return 'CSV'
        elif extension in ['.xls', '.xlsx', '.xlsm']: return 'Excel'
        else: raise TypeError(f'The .{extension} filetype is not supported.')

    def _labels(self, label_row):
        """Grab the labels from the specified row."""

        # Grab the labels using the appropriate method for the filetype
        if self._type == 'CSV':
            labels = pd.read_csv(self.filepath, skiprows=label_row-1, nrows=1,
                                 index_col=False, header=None)
        elif self._type == 'Excel':
            labels = pd.read_excel(self.filepath, skiprows=label_row-1, nrows=1,
                                   index_col=False, header=None, encoding='latin1')
        # Convert the pandas dataframe to a list and return it
        return list(labels.values.flatten())

    def _units(self, unit_row):
        """Grab the units from the specified row."""

        # If the unit_row parameter is None, do not continue
        if not unit_row: return None

        # Grab the units using the appropriate method for the filetype
        if self._type == 'CSV':
            units = pd.read_csv(self.filepath, skiprows=unit_row-1, nrows=1,
                                index_col=False, header=None)
        elif self._type == 'Excel':
            units = pd.read_excel(self.filepath, skiprows=unit_row-1, nrows=1,
                                  index_col=False, header=None, encoding='latin1')
        # Convert the pandas dataframe to a list and return it
        return list(units.values.flatten())

    def _data(self, data_start_row):
        """Grab the appropriate data from the file."""

        # Read the file using the appropriate method for the filetype
        if self._type == 'CSV':
            return pd.read_csv(self.filepath, skiprows=data_start_row-1,
                                 names=self.labels, index_col=False,
                                 header=None)
        elif self._type == 'Excel':
            return pd.read_excel(self.filepath, skiprows=data_start_row-1,
                                 names=self.labels, index_col=False,
                                 header=None, encoding='latin1')

    def generate(self):
        """The main function for the object which pulls all of the relevant data
        from the file and adds the appropriate information to the plot objects."""

        # Determine the file's type
        self._type = self._filetype(self.filepath)

        # Store the label row and corresponding labels as instance variables
        self.label_row = int(self.label_row_entry.get())
        self.labels = self._labels(self.label_row)

        # Store the unit row and corresponding units as instance variables
        self.unit_row = int(self.unit_row_entry.get()) if self.unit_row_entry.get() else None
        self.units = self._units(self.unit_row)

        # Store the data start row and corresponding data as instance variables
        self.data_start_row = int(self.data_row_entry.get())
        self.data = self._data(self.data_start_row)

        # Iterate through each plot
        for p, plot in enumerate(self.plots):
            # Grab all entries in each field
            title = self._titles[p].get()
            x_column = int(self._x_columns[p].get())
            self.y1_columns = [int(item) for item in re.findall(r'\d+', self._y1_columns[p].get())]
            self.y2_columns = [int(item) for item in re.findall(r'\d+', self._y2_columns[p].get())]
            x_label = self._x_labels[p].get()
            y1_label = self._y1_labels[p].get()
            y2_label = self._y2_labels[p].get()
            # Feed the entries to the plot object
            plot._generate(self.data, self.labels, x_column, self.y1_columns,
                           self.y2_columns, self.units)
            plot._labels(title, x_label, y1_label, y2_label)


class Flipbook(tk.Toplevel):
    """The flipbook is where the plots and relevant information are shown. The main feature
    of the flipbook is that you are able to quickly and easily move through a series of
    plots by pressing the left button (or arrow key) or right button (or arrow key)."""

    def __init__(self, *args, info, **kwargs):
        """Create the flipbook GUI and perform any initialization that needs to be done."""

        def on_close():
            """When the flipbook is closed, redisplay the main window as well."""

            self.destroy()
            app.root.deiconify()
            app.FLIPBOOK = False


        def show_controls():
            """Refresh the controls window and make it visible."""

            self.controls.refresh()
            self.controls.deiconify()


        # Initialize variables
        self.info = info # Make the information that was passed in accessible elsewhere
        self.page = 0 # Current page number
        self.pages = sum(file._count for file in info) - 1 # Index of the last page
        self.secondary = None # Secondary axis
        self.controls = None # Controls window

        # Get a list of plots, files, and plot numbers.
        # self.plots --> a list of all plots in each file, meant to make it easier to move
        #                between plots by simply incrementing the page number
        # self.files --> list of numbers that links each plot in self.plots to its corresponding
        #                file index
        # self.numbers --> list of numbers that enumerates each plot in self.plots with respect
        #                  to its corresponding file
        self.plots = [plot for file in self.info for plot in file.plots]
        self.files = [f for f, file in enumerate(self.info) for _ in range(len(file.plots))]
        self.numbers = [p for f, file in enumerate(self.info) for p in range(len(file.plots))]

        # Initialize the flipbook as a top-level window and immediately hide it
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.withdraw()
        self.title('Flipbook')
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", on_close)

        # Create a padded frame to keep all of the widgets in
        flipbook = gui.PaddedFrame(self)
        flipbook.grid(row=0, column=0, sticky='NSEW')

        # Create the frame that will hold the 'flip left' button
        left = tk.Frame(flipbook)
        left.grid(row=0, column=0, padx=(0, 12), sticky='NSEW')
        left.rowconfigure(0, weight=1)
        self.previous_button = ttk.Button(left, text='◀', width=3, takefocus=0)
        self.previous_button.grid(row=0, column=0, sticky='NSEW')
        self.previous_button['command'] = lambda event=None, direction='left': \
                                          self.flip_page(event, direction)

        # Create the frame that will hold the 'flip right' button
        right = tk.Frame(flipbook)
        right.grid(row=0, column=2, padx=(12, 0), sticky='NSEW')
        right.rowconfigure(0, weight=1)
        self.next_button = ttk.Button(right, text='▶', width=3, takefocus=0)
        self.next_button.grid(row=0, column=0, sticky='NSEW')
        self.next_button['command'] = lambda event=None, direction='right': \
                                      self.flip_page(event, direction)

        # Define the color to be used for the plot
        middle_color = '#e6e6e6'

        # Create the frame that the plot and its controls will be held in
        middle = tk.Frame(flipbook, bg=middle_color)
        middle.grid(row=0, column=1, sticky='NSEW')
        middle.columnconfigure(0, minsize=800)

        # Create a figure and the primary axis
        self.figure = Figure(figsize=(12, 7), dpi=100)
        self.primary = self.figure.add_subplot(111)

        # Change the face color of the figure and adjust the padding
        self.figure.patch.set_facecolor(middle_color)
        self.figure.subplots_adjust(top=0.90, bottom=0.15)

        # Place a canvas on the figure and update it
        self.canvas = FigureCanvasTkAgg(self.figure, middle)
        self.canvas.draw()

        # Create a frame that will hold the toolbar and the controls button
        toolbar_frame = tk.Frame(middle)
        toolbar_frame.grid(row=0, column=0, sticky='NSEW')
        toolbar_frame.columnconfigure(0, weight=1)

        # Create a toolbar that can be used for manipulating the plot
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.config(bg=middle_color)
        toolbar._message_label.config(bg=middle_color)
        toolbar.update()
        toolbar.grid(row=0, column=0, sticky='NSEW')

        # # Create the controls button that allows the user to open the controls window
        # controls_image = gui.RenderImage(gui.ResourcePath('Assets\\controls.png'), downscale=9)
        # controls_button = ttk.Button(toolbar_frame, text='Controls', takefocus=0,
        #                              image=controls_image, command=show_controls)
        # controls_button.grid(row=0, column=1, sticky='E')
        # controls_button.image = controls_image

        # Create a label that will display the filename of the current plot's corresponding file
        self.filename = tk.StringVar()
        filename_label = tk.Label(middle, textvar=self.filename,
                                  font=('Helvetica', 18, 'bold'),
                                  anchor='w', bg=middle_color)
        filename_label.grid(row=1, column=0, sticky='EW')

        # Create the graph widget where the plot will be displayed
        graph_widget = self.canvas.get_tk_widget()
        graph_widget.grid(row=2, column=0, sticky='NSEW')

        # Create keyboard shortcuts that allow for flipping between pages with the arrow keys
        self.bind('<Left>',
                  lambda event, direction='left': self.flip_page(event, direction))
        self.bind('<Right>',
                  lambda event, direction='right': self.flip_page(event, direction))

        # Add call the on_click method whenever the user clicks on a clickable object
        self.canvas.mpl_connect('pick_event', self.on_click)

        # Update the arrows and the plot of the flipbook
        self.update_arrows()
        self.update_plot()

        # Make the flipbook visible again and center it on the screen
        self.deiconify()
        gui.CenterWindow(self)


    def update_plot(self):
        """Update the plot with new data or information."""

        current = self.plots[self.page] # Current plot object
        file_number = self.files[self.page] # File index
        plot_number = self.numbers[self.page] # Plot number in file

        # fileclass = self.info[self.page].__class__.__name__
        # if self.controls and fileclass != 'BasicFile':
        #     # self.controls.disable()
        #     print('the controls window would be disabled right now')
        #     return

        # self.controls.disable()

        # Update the plot using the plot object's update_plot method
        current.update_plot(self, file_number, plot_number)

        # Update the canvas
        self.canvas.draw()


    def update_arrows(self):
        """Update the arrows of the flipbook when the page is changed."""

        # If the current page is the first page, disable the 'flip left' button
        if self.page == 0:
            self.previous_button.config(state='disabled')
        # If the current page is the last page, disable the 'flip right' button
        if self.page == self.pages:
            self.next_button.config(state='disabled')
        # If the current page is somewhere in between, enable both flip buttons
        if 0 < self.page < self.pages:
            self.previous_button.config(state='normal')
            self.next_button.config(state='normal')


    def flip_page(self, event, direction):
        """Flip between pages of the flipbook."""

        # Determine the destination page
        destination = (self.page + 1) if direction == 'right' else (self.page - 1)
        # If the destination page is within the range of the total number of pages...
        if destination in range(self.pages + 1):
            # Set the new page number; update arrows and the plot
            self.page += 1 if direction == 'right' else -1
            # self.controls.current = self.plots[self.page]
            self.update_plot()
            self.update_arrows()
            # # Refresh the controls window
            # self.controls.refresh()

        # Return 'break' to bypass event propagation
        return ('break')


    def on_click(self, event):
        """Hide or show a line when the corresponding object in the legend is clicked."""

        # Get a reference to the legend line and the original line
        legend_line = event.artist
        original_line = self.line_map[legend_line]
        # Determine whether to show or hide the original line
        visible = not original_line.get_visible()
        # Set the visibility accordingly
        original_line.set_visible(visible)
        legend_line.set_alpha(1.0 if visible else 0.2)
        # Update the plot
        self.canvas.draw()


    def _coordinates(self, current, other, secondary_exists):
        """Determine the appropriate coordinate format to use for the number of axes.
        Current is the axis that is being formatted; other is the axis that is not being
        formatted; secondary_exists is a boolean value, where True means that a secondary
        axis exists, while False means it does not."""

        if secondary_exists:
            def format_coord(x, y):
                """Create the appropriate coordinate formatting if both axes exist,
                where x and y are data coordinates passed to this function by the mouse
                event of matplotlib."""

                # Secondary axis coordinates have been passed into this function already
                secondary = (x, y)
                # Convert data coordinates of the secondary axis to display coordinates
                display = current.transData.transform(secondary)
                # Invert the primary axis coordinates
                inverted = other.transData.inverted()
                # Convert to data coords with respect to the display coordinates
                primary = inverted.transform(display)
                # Combine the coordinates into a list and return the formatted string
                coords = [primary, secondary]
                return ('Primary: {:<}  |  Secondary: {:<}'
                            .format(*['({:.3f}, {:.3f})'.format(x, y) for x, y in coords]))

        elif not secondary_exists:
            def format_coord(x, y):
                """Create the appropriate coordinate formatting if only the primary
                axis exists, where x and y are data coordinates passed to this function
                by matplotlib."""

                # Return the formatted string
                return ('Primary: ({:<.3f}, {:<.3f})'.format(x, y))

        # Return the approprate coordinates format function
        return format_coord


class Controls(tk.Toplevel):

    def __init__(self, master, current):
        """Create a controls window where the user can adjust the plot."""

        def custom_background(event=None):
            """Allow the user to navigate to and select a custom background.

            This function is called whenever an option in the appropriate combobox is
            selected. However, its purposes is to only execute when the 'Custom'
            option is selected."""

            # Get a reference to the current plot
            current = self.current
            # If the user chooses to use a custom background...
            if self.background_choice.get() == 'Custom':
                # Get the filepath of the selected file
                path = fd.askopenfilename(title='Select the background image')
                if path:
                    # If the user follows through, save the filepath
                    current.background_path = path
                else:
                    # If the user cancels, set the plot's background_path attribute to None
                    # as well as the combobox value.
                    current.background_path = None
                    self.background_choice.set('None')
            else:
                # Otherwise, set the current plot's background_path attribute to None
                current.background_path = None

        # Create the top-level controls window
        tk.Toplevel.__init__(self, master)
        self.title('Controls')
        self.resizable(width=False, height=False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # When the user closes the controls window, just hide it instead
        self.protocol("WM_DELETE_WINDOW", lambda: self.withdraw())

        # Initialize miscellaneous instance variables
        self.flipbook = master
        self.current = current
        self.band_controls = None # Tolerance band controls object
        self.line_controls = None # Limit lines controls object

        # Create the primary frame, which will hold the notebook and provide padding
        primary = gui.PaddedFrame(self)
        primary.grid(row=0, column=0, sticky='NSEW')
        primary.columnconfigure(0, weight=1)
        primary.rowconfigure(0, weight=1)

        # Create the notebook which will contain tabs for all controls
        notebook = ttk.Notebook(primary, takefocus=0)
        notebook.grid(row=0, column=0, sticky='NSEW')
        # Add scrollable tabs to the notebook
        figure = gui.ScrollableTab(notebook, 'Figure', cheight=400, cwidth=400)
        appearance = gui.ScrollableTab(notebook, 'Appearance', cheight=400, cwidth=400)
        analysis = gui.ScrollableTab(notebook, 'Analysis', cheight=400, cwidth=400)
        annotations = gui.ScrollableTab(notebook, 'Annotations', cheight=400, cwidth=400)

        # Separate the primary and secondary frames
        gui.Separator(self).grid(row=1, column=0, sticky='NSEW')

        # Create the secondary frame which will contain the update button
        secondary = gui.PaddedFrame(self)
        secondary.grid(row=2, column=0, sticky='NSEW')
        secondary.columnconfigure(0, weight=1)

        # Create the update button
        update_button = ttk.Button(secondary, text='Update', takefocus=0,
                                   command=self.update)
        update_button.grid(row=0, column=0, sticky='E')

        # ==========
        # FIGURE TAB
        # ==========

        # Create the limits frame which will hold fields for each axis limit
        limits = gui.PaddedFrame(figure)
        limits.grid(row=0, column=0, sticky='NSEW')
        limits.columnconfigure(0, weight=1)
        limits.columnconfigure(1, weight=1)
        # Define amount of padding to use around widgets
        LIMITS_PADDING = 10
        # Add the title of the section
        limits_title = tk.Label(limits, text='Axis Limits',
                         font=('TkDefaultFont', 10, 'bold'))
        limits_title.grid(row=0, column=0, pady=(0, 10), sticky='W')
        # Create a lower x-axis label and entry
        x_lower_label = tk.Label(limits, text='x-lower:')
        x_lower_label.grid(row=1, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        self.x_lower_entry = ttk.Entry(limits, width=20)
        self.x_lower_entry.grid(row=2, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        # Create an upper x-axis label and entry
        x_upper_label = tk.Label(limits, text='x-upper:')
        x_upper_label.grid(row=1, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        self.x_upper_entry = ttk.Entry(limits, width=20)
        self.x_upper_entry.grid(row=2, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        # Add some vertical spacing between widgets
        gui.Space(limits, row=3, column=0, columnspan=2)
        # Create a lower y1-axis label and entry
        y1_lower_label = tk.Label(limits, text='y1-lower:')
        y1_lower_label.grid(row=4, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        self.y1_lower_entry = ttk.Entry(limits, width=20)
        self.y1_lower_entry.grid(row=5, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        # Create an upper y1-axis label and entry
        y1_upper_label = tk.Label(limits, text='y1-upper:')
        y1_upper_label.grid(row=4, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        self.y1_upper_entry = ttk.Entry(limits, width=20)
        self.y1_upper_entry.grid(row=5, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        # Add some vertical spacing between widgets
        gui.Space(limits, row=6, column=0, columnspan=2)
        # Create a lower y2-axis label and entry
        y2_lower_label = tk.Label(limits, text='y2_lower:')
        y2_lower_label.grid(row=7, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        self.y2_lower_entry = ttk.Entry(limits, width=20)
        self.y2_lower_entry.grid(row=8, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        # Create an upper y2-axis label and entry
        y2_upper_label = tk.Label(limits, text='y2_upper:')
        y2_upper_label.grid(row=7, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        self.y2_upper_entry = ttk.Entry(limits, width=20)
        self.y2_upper_entry.grid(row=8, column=1, padx=LIMITS_PADDING, sticky='NSEW')

        # Add a separator
        separator = gui.Separator(figure, orientation='horizontal', padding=(0, (10, 0)))
        separator.grid(row=1, column=0, sticky='NSEW')

        # Create the ticks frame which will hold fields for each axis tick field
        ticks = gui.PaddedFrame(figure)
        ticks.grid(row=2, column=0, sticky='NSEW')
        ticks.columnconfigure(0, weight=1)
        ticks.columnconfigure(1, weight=1)
        # Add the title of the section
        ticks_title = tk.Label(ticks, text='Axis Ticks',
                         font=('TkDefaultFont', 10, 'bold'))
        ticks_title.grid(row=0, column=0, pady=(0, 10), sticky='W')
        # Create a label and an entry for the primary ticks
        primary_ticks_label = tk.Label(ticks, text='Primary ticks:')
        primary_ticks_label.grid(row=1, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        self.primary_ticks_entry = ttk.Entry(ticks)
        self.primary_ticks_entry.grid(row=2, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        # Create a label and an entry for the secondary ticks
        secondary_ticks_label = tk.Label(ticks, text='Secondary ticks:')
        secondary_ticks_label.grid(row=1, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        self.secondary_ticks_entry = ttk.Entry(ticks)
        self.secondary_ticks_entry.grid(row=2, column=1, padx=LIMITS_PADDING, sticky='NSEW')

        # ==============
        # APPEARANCE TAB
        # ==============

        general = gui.PaddedFrame(appearance)
        general.grid(row=0, column=0, sticky='NSEW')
        general.columnconfigure(0, weight=1)
        general.columnconfigure(1, weight=1)

        # Add the title of the section
        general_title = tk.Label(general, text='General Appearance',
                         font=('TkDefaultFont', 10, 'bold'))
        general_title.grid(row=0, column=0, pady=(0, 10), columnspan=2, sticky='W')

        # Create a padded frame for the background controls
        background = tk.Frame(general)
        background.grid(row=1, column=0, sticky='NSEW')
        background.columnconfigure(0, weight=1)
        # Add a label for the background combobox
        background_label = tk.Label(background, text='Background:')
        background_label.grid(row=0, column=0, padx=10, sticky='NSEW')
        # Add a combobox to control the background of the plot
        self.background_choice = tk.StringVar()
        background_combo = ttk.Combobox(background, width=20, state='readonly',
                                        textvariable=self.background_choice)
        background_combo.grid(row=1, column=0, padx=10, sticky='NSEW')
        background_combo['values'] = ['None', 'Tactair', 'Young & Franklin', 'Custom']
        background_combo.bind('<<ComboboxSelected>>', custom_background)

        # Create a padded frame for the style controls
        style = tk.Frame(general)
        style.grid(row=1, column=1, sticky='NSEW')
        style.columnconfigure(0, weight=1)
        # Add a label for the style combobox
        style_label = tk.Label(style, text='Style:')
        style_label.grid(row=0, column=0, padx=10, sticky='NSEW')
        # Add a combobox to control the style of the plot
        self.style_choice = tk.StringVar()
        style_combo = ttk.Combobox(style, width=20, state='readonly',
                                        textvariable=self.style_choice)
        style_combo.grid(row=1, column=0, padx=10, sticky='NSEW')
        style_combo['values'] = ['Default', 'Classic', 'Seaborn', 'Fivethirtyeight']

        # ============
        # ANALYSIS TAB
        # ============

        # Create a frame that will hold the dynamic tolerance bands controls
        self.tolerance_bands = gui.PaddedFrame(analysis)
        self.tolerance_bands.grid(row=0, column=0, sticky='NSEW')
        self.tolerance_bands.columnconfigure(0, weight=1)

        # ===============
        # ANNOTATIONS TAB
        # ===============

        # Create a frame that will hold the dynamic limit lines controls
        self.horizontal_lines = gui.PaddedFrame(annotations)
        self.horizontal_lines.grid(row=0, column=0, sticky='NSEW')
        self.horizontal_lines.columnconfigure(0, weight=1)

        # ===============
        # END OF CONTROLS
        # ===============

        # Refresh the controls with values for the current plot
        self.refresh()

        # Bind the enter key to the same function the update button calls
        self.bind('<Return>', self.update)


    def refresh(self):
        """Refresh the controls window fields with the currently stored values."""

        # Get a reference to the current plot object
        current = self.current

        # ====================
        # AXES LIMITS CONTROLS
        # ====================

        def fill_entry(entry, value, original):
            """Clear the entry and insert the changed value if it exists, otherwise
            insert the original value."""

            entry.delete(0, 'end')
            entry.insert(0, value if value else original)

        # Fill in each field with their respective values
        fill_entry(self.x_lower_entry, current.x_lower, current.x_lower_original)
        fill_entry(self.x_upper_entry, current.x_upper, current.x_upper_original)
        fill_entry(self.y1_lower_entry, current.y1_lower, current.y1_lower_original)
        fill_entry(self.y1_upper_entry, current.y1_upper, current.y1_upper_original)
        # Disable the secondary axis entry fields if there is no secondary axis,
        # otherwise enable and fill the entry fields corresponding to the secondary axis.
        if current.secondary_axis:
            self.y2_lower_entry['state'] = 'normal'
            fill_entry(self.y2_lower_entry, current.y2_lower, current.y2_lower_original)
            self.y2_upper_entry['state'] = 'normal'
            fill_entry(self.y2_upper_entry, current.y2_upper, current.y2_upper_original)
        else:
            self.y2_lower_entry.delete(0, 'end')
            self.y2_lower_entry['state'] = 'disabled'
            self.y2_upper_entry.delete(0, 'end')
            self.y2_upper_entry['state'] = 'disabled'

        # ===================
        # AXIS TICKS CONTROLS
        # ===================

        # Fill the primary and secondary tick fields with the appropriate stored value
        fill_entry(self.primary_ticks_entry, current.primary_ticks, '')
        fill_entry(self.secondary_ticks_entry, current.secondary_ticks, '')
        # Disable the secondary axis entry field if there is no secondary axis,
        # otherwise enable and fill the entry fields corresponding to the secondary axis.
        if current.secondary_axis:
            self.secondary_ticks_entry['state'] = 'normal'
            fill_entry(self.secondary_ticks_entry, current.secondary_ticks, '')
        else:
            self.secondary_ticks_entry.delete(0, 'end')
            self.secondary_ticks_entry['state'] = 'disabled'

        # ========================
        # STYLE SELECTION CONTROLS
        # ========================

        # Set the current style combobox selection to the stored style value
        self.style_choice.set(current.style.get())

        # =============================
        # BACKGROUND SELECTION CONTROLS
        # =============================

        # Set the current background combobox selection to the stored background value
        self.background_choice.set(current.background.get())

        # =======================
        # TOLERANCE BAND CONTROLS
        # =======================

        # If the band_controls widget already exists, remove it from view.
        # Destroying it will cause the program to not be able to reference those fields.
        if self.band_controls: self.band_controls.grid_forget()
        # Re-grid the tolerance bands object of the current plot
        self.band_controls = current.bands
        self.band_controls.setup(self.tolerance_bands)
        self.band_controls.grid(row=0, column=0, sticky='NSEW')

        # If the attributes of the current plot object have been changed...
        if current.series and current.minus_tolerance and current.plus_tolerance and current.lag:
            # Determine which of those lists is the longest and recreate that many rows
            longest = len(max(current.series, current.minus_tolerance,
                              current.plus_tolerance, current.lag))
            self.band_controls.recreate(rows=longest)

        # Fill the newly create entries with the relevant values
        self.band_controls.series = current.series
        self.band_controls.color = current.color
        self.band_controls.linestyle = current.linestyle
        self.band_controls.plus_tolerance = current.plus_tolerance
        self.band_controls.minus_tolerance = current.minus_tolerance
        self.band_controls.lag = current.lag
        self.band_controls.bands_plus = current.plus_bands
        self.band_controls.bands_minus = current.minus_bands

        # Every time the combobox is selected, update its options with the currently
        # plotted columns.
        values = []
        for column in current.y1_columns:
            values.append(current.labels[column-1])
        for column in current.y2_columns:
            values.append(current.labels[column-1])
        self.band_controls.update_series(values)

        # ===================
        # LIMIT LINE CONTROLS
        # ===================

        # If the band_controls widget already exists, remove it from view.
        # Destroying it will cause the program to not be able to reference those fields.
        if self.line_controls: self.line_controls.grid_forget()
        # Re-grid the tolerance bands object of the current plot
        self.line_controls = current.lines
        self.line_controls.setup(self.horizontal_lines)
        self.line_controls.grid(row=0, column=0, sticky='NSEW')

        # If the attributes of the current plot object have been changed...
        if current.line_orientation and current.line_axis and current.line_value and \
                current.line_color and current.line_alpha:
            # Determine which of those lists is the longest and recreate that many rows
            longest = len(max(current.line_orientation, current.line_axis, current.line_style,
                              current.line_value, current.line_color, current.line_alpha))
            self.line_controls.recreate(rows=longest)

        # Fill the newly create entries with the relevant values
        self.line_controls.axis = current.line_axis
        self.line_controls.orientation = current.line_orientation
        self.line_controls.value = current.line_value
        self.line_controls.color = current.line_color
        self.line_controls.linestyle = current.line_style
        self.line_controls.alpha = current.line_alpha


    def update(self, event=None):
        """Update the current plot object with the user-entered values and refresh
        both the plot and the controls window."""

        # Get a reference to the current plot object
        current = self.current

        # ====================
        # AXES LIMITS CONTROLS
        # ====================

        def update_axis(entry, original):
            """If a value was changed, convert it from a string to a float. Otherwise,
            use the original value."""

            return float(entry.get()) if entry.get() else float(original)

        # Store the axes limits values in the corresponding plot object attributes
        current.x_lower = update_axis(self.x_lower_entry, current.x_lower_original)
        current.x_upper = update_axis(self.x_upper_entry, current.x_upper_original)
        current.y1_lower = update_axis(self.y1_lower_entry, current.y1_lower_original)
        current.y1_upper = update_axis(self.y1_upper_entry, current.y1_upper_original)
        if current.secondary_axis:
            current.y2_lower = update_axis(self.y2_lower_entry, current.y2_lower_original)
            current.y2_upper = update_axis(self.y2_upper_entry, current.y2_upper_original)

        # ===================
        # AXIS TICKS CONTROLS
        # ===================

        # Store the values in the primary and secondary tick fields
        current.primary_ticks = self.primary_ticks_entry.get()
        current.secondary_ticks = self.secondary_ticks_entry.get()

        # ========================
        # STYLE SELECTION CONTROLS
        # ========================

        # Store the currently selected value from the style combobox
        current.style.set(self.style_choice.get())

        # =============================
        # BACKGROUND SELECTION CONTROLS
        # =============================

        # Store the currently selected value from the background combobox
        current.background.set(self.background_choice.get())

        # =======================
        # TOLERANCE BAND CONTROLS
        # =======================

        # Store the current band controls values in the corresponding plot attributes
        current.series = self.band_controls.series
        current.linestyle = self.band_controls.linestyle
        current.color = self.band_controls.color
        current.plus_tolerance = self.band_controls.plus_tolerance
        current.minus_tolerance = self.band_controls.minus_tolerance
        current.lag = self.band_controls.lag
        current.plus_bands = self.band_controls.bands_plus
        current.minus_bands = self.band_controls.bands_minus

        # Pass the current plot object to the calculate method to create the bands
        self.band_controls.calculate(current)

        # ===================
        # LIMIT LINE CONTROLS
        # ===================

        # Store the current limit line values in the corresponding plot attributes
        current.line_axis = self.line_controls.axis
        current.line_orientation = self.line_controls.orientation
        current.line_value = self.line_controls.value
        current.line_color = self.line_controls.color
        current.line_style = self.line_controls.linestyle
        current.line_alpha = self.line_controls.alpha

        # Update the plot and refresh the controls window
        self.flipbook.update_plot()
        self.refresh()


class ToleranceBands(tk.Frame):
    """Creates a GUI frame that can hold a dynamic amount of rows for
    tolerance band fields. Keeps track of inputs and band data as well."""

    def __init__(self):
        """Initialize the object's attributes."""

        # Initialize/reset the object's attributes
        self.reset()

    def setup(self, master):
        """Create the toolbar of the Tolerance Bands object. This function is called
        every time the page is flipped."""

        # Initialize the Tolerance Bands object as a frame
        tk.Frame.__init__(self, master=master)
        self.columnconfigure(0, weight=1)

        # Create a controls frame, which will function as a toolbar
        controls = tk.Frame(self)
        controls.grid(row=0, column=0, sticky='NSEW')
        controls.columnconfigure(0, weight=1)

        # Add the title of the section
        title = tk.Label(controls, text='Tolerance Bands',
                         font=('TkDefaultFont', 10, 'bold'))
        title.grid(row=0, column=0, sticky='W')

        # Add a button that adds another row to the object
        add_button = ttk.Button(controls, text='+', width=3, takefocus=0,
                                command=self.add_band)
        add_button.grid(row=0, column=1)

        # Add a button that deletes a row from the object
        delete_button = ttk.Button(controls, text='-', width=3, takefocus=0,
                                   command=self.delete_band)
        delete_button.grid(row=0, column=2)

    def reset(self):
        """Reset the attributes of the object to their default states. Called
        whenever a Tolerance Bands object is created or recreated."""

        # Reset the row count to 0
        self.count = 0
        # Reset the bands list, which holds a reference to each row
        self.bands = []
        # Reset the choices list for the series combobox and the color combobox
        self.series_choices = []
        self.color_choices = []
        self.linestyle_choices = []
        # Reset the lists that hold references to each field of each row
        self.series_combos = []
        self.minus_tolerance_entries = []
        self.plus_tolerance_entries = []
        self.lag_entries = []
        self.color_combos = []
        self.linestyle_combos = []
        # Reset the values that appear in the series combobox
        self.values = None
        # Clear the data for the plus tolerance and minus tolerance bands
        self.plus_bands = []
        self.minus_bands = []

    def recreate(self, rows):
        """Recreates the rows that were previously in the Tolerance Bands object
        before the page was flipped. The rows parameter is calculated outside of
        the purview of this object and then passed in."""

        # Minus and plus bands should not be reset when flipping a page, so store
        # them in a backup variable for now
        self.minus_backup = self.minus_bands
        self.plus_backup = self.plus_bands
        # Reset the object's attributes
        self.reset()
        # Add as many rows as there were before the page was flipped
        for row in range(rows):
            self.add_band(recreate=row)
        # Set the minus and plus band data back to what they were before the reset
        self.minus_bands = self.minus_backup
        self.plus_bands = self.plus_backup

    def add_band(self, recreate=None):
        """Add a row to the Tolerance Bands object."""

        # Define the general amount of padding to use between widgets
        PADDING = 2

        # Create a frame that will hold all of the fields
        frame = tk.LabelFrame(self)
        frame.grid(row=self.count+1 if not recreate else recreate+1,
                   column=0, pady=(10, 0))

        # Put a frame inside of the labelframe, but with padding
        container = tk.Frame(frame)
        container.grid(row=0, column=0, padx=10, pady=10, sticky='NSEW')

        # Specify a general width for combobox and entry widgets
        COMBO_WIDTH = 14
        ENTRY_WIDTH = 17

        # Add labels for series, plus and minus tolerance, lag, and color
        series_label = ttk.Label(container, text='series:')
        series_label.grid(row=0, column=0, padx=PADDING)

        color_label = ttk.Label(container, text='color:')
        color_label.grid(row=0, column=1, padx=PADDING)

        linestyle_label = ttk.Label(container, text='linestyle:')
        linestyle_label.grid(row=0, column=2, padx=PADDING)

        plus_tolerance_label = ttk.Label(container, text='+tolerance:')
        plus_tolerance_label.grid(row=2, column=0, padx=PADDING)

        minus_tolerance_label = ttk.Label(container, text='-tolerance:')
        minus_tolerance_label.grid(row=2, column=1, padx=PADDING)

        lag_label = ttk.Label(container, text='lag:')
        lag_label.grid(row=2, column=2, padx=PADDING)

        # Add a combobox to select which series to plot the bands around
        series_choice = tk.StringVar()
        series_combo = ttk.Combobox(container, width=COMBO_WIDTH, state='readonly',
                                    textvariable=series_choice,
                                    postcommand=self.update_entries)
        series_combo.grid(row=1, column=0, padx=PADDING)
        self.series_choices.append(series_choice)
        self.series_combos.append(series_combo)

        # Add a combobox to select which color the bands should be
        color_choice = tk.StringVar()
        color_choice.set(random.choice(list(app.plot_colors.keys())))
        color_combo = ttk.Combobox(container, textvariable=color_choice,
                                   width=COMBO_WIDTH, state='readonly')
        color_combo['values'] = list(app.plot_colors.keys())
        color_combo.grid(row=1, column=1, padx=PADDING)
        self.color_choices.append(color_choice)
        self.color_combos.append(color_combo)

        # Add a combobox to select which color the bands should be
        linestyle_choice = tk.StringVar()
        linestyle_choice.set('solid')
        linestyle_combo = ttk.Combobox(container, textvariable=linestyle_choice,
                                   width=COMBO_WIDTH, state='readonly')
        linestyle_combo['values'] = ['solid', 'dashed', 'dashdot', 'dotted']
        linestyle_combo.grid(row=1, column=2, padx=PADDING)
        self.linestyle_choices.append(linestyle_choice)
        self.linestyle_combos.append(linestyle_combo)

        # Add an entry where the user can specify plus tolerance
        plus_tolerance_entry = ttk.Entry(container, width=ENTRY_WIDTH)
        plus_tolerance_entry.grid(row=3, column=0, padx=PADDING)
        self.plus_tolerance_entries.append(plus_tolerance_entry)

        # Add an entry where the user can specify minus tolerance
        minus_tolerance_entry = ttk.Entry(container, width=ENTRY_WIDTH)
        minus_tolerance_entry.grid(row=3, column=1, padx=PADDING)
        self.minus_tolerance_entries.append(minus_tolerance_entry)

        # Add an entry where the user can specify lag
        lag_entry = ttk.Entry(container, width=ENTRY_WIDTH)
        lag_entry.grid(row=3, column=2, padx=PADDING)
        self.lag_entries.append(lag_entry)

        # If this method was not called by the recreate function, add filler
        # data to the plus bands and minus bands data lists
        if not recreate:
            self.plus_bands.append(None)
            self.minus_bands.append(None)

        # Add one to the row count and keep a reference to this row
        self.count += 1
        self.bands.append(frame)

    def delete_band(self):
        """Remove a row from the Tolerance Bands object."""

        # If there are already no rows, exit the method
        if len(self.bands) == 0: return

        # Destroy the last row and remove all references to the objects
        self.bands[-1].destroy()
        del(self.bands[-1])
        del(self.series_choices[-1])
        del(self.series_combos[-1])
        del(self.color_choices[-1])
        del(self.color_combos[-1])
        del(self.linestyle_choices[-1])
        del(self.linestyle_combos[-1])
        del(self.minus_tolerance_entries[-1])
        del(self.plus_tolerance_entries[-1])
        del(self.lag_entries[-1])
        del(self.minus_bands[-1])
        del(self.plus_bands[-1])
        # Decrease the row count by one
        self.count -= 1

    def update_series(self, values):
        """Update the variables that stores which series are currently plotted.
        Meant to be called from outside the purview of the object."""

        # Set the self.values variable to the list that was passed in
        self.values = values

    def update_entries(self):
        """Updates the combobox to list the series that are currently plotted."""

        # Iterate through each series combobox in each row and update its options
        for combo in self.series_combos:
            combo['values'] = self.values

    def calculate(self, plot):
        """Takes the inputs from each row and calculates tolerance band data from it."""

        def BandData(iterator, which):
            """Calculate tolerance band data. Which is either '+' for the plus tolerance
            band or '-' for the minus tolerance band."""

            def get_value(entry):
                """Return the contents of the entry as a float if something has been
                entered, otherwise return 0."""

                return float(entry.get()) if entry.get() else 0

            # Grab the minus tolerance, plus tolerance, and lag values
            MINUS_TOLERANCE = get_value(self.minus_tolerance_entries[iterator])
            PLUS_TOLERANCE = get_value(self.plus_tolerance_entries[iterator])
            LAG = get_value(self.lag_entries[iterator])

            # Grab the selected series from the appropriate series combobox
            series = self.series_combos[iterator].get()

            # Find the index of the selection within the list of the current plot's labels
            index = plot.labels.index(series)

            # Determine which axis the series is plotted on and then determine the index
            # of the series within that axis's column list
            if index + 1 in plot.y1_columns:
                axis = 'primary'
                position = plot.y1_columns.index(index + 1)
            else:
                axis = 'secondary'
                position = plot.y2_columns.index(index + 1)

            # Get a reference to the x-data and y-data
            x = plot.x
            if axis == 'primary':
                y = plot.y1[position]
            elif axis == 'secondary':
                y = plot.y2[position]

            # Define the lookback range
            resolution = x[1] - x[0]
            lookback = round(LAG / resolution)

            # Iterate through the y-data and begin tolerance bands calculations once the
            # index is greater than the lookback range. Essentially, The lookback range
            # accounts for the lag/time shift, and then the appropriate tolerance is added
            # or subtracted on top of that. The tolerance band data will be of the same
            # length as the y-data, but the first few values may be None.
            band = []
            for i, c in enumerate(y):
                if i >= lookback:
                    if which == '+':
                        # Get the maximum value in the lookback range and add tolerance
                        maximum = max(y.loc[i-lookback:i])
                        toleranced = maximum + PLUS_TOLERANCE
                    elif which == '-':
                        # Get the minimum value in the lookback range and subtract tolerance
                        minimum = min(y.loc[i-lookback:i])
                        toleranced = minimum - MINUS_TOLERANCE
                    band.append(toleranced)
                else:
                    # Don't want to plot any values before a lookback can be done
                    band.append(None)

            # Return the axis that the series on plotted on as well as the band data
            return (axis, band)

        # For each row, create data for a plus band and a minus band
        for i in range(len(self.series_combos)):
            self.plus_bands[i] = BandData(i, which='+')
            self.minus_bands[i] = BandData(i, which='-')

    @property
    def series(self):
        """Iterates through each row and returns a list of series combobox selections."""

        return [combo.get() for combo in self.series_combos]

    @series.setter
    def series(self, series):
        """Sets the value of each series combobox with the appropriate value."""

        if series:
            for i in range(len(series)):
                self.series_choices[i].set(series[i] if series[i] else '')

    @property
    def color(self):
        """Iterates through each row and returns a list of color combobox selections."""

        return [combo.get() for combo in self.color_combos]

    @color.setter
    def color(self, colors):
        """Sets the value of each color combobox with the appropriate value."""

        if colors:
            for i in range(len(colors)):
                self.color_choices[i].set(colors[i] if colors[i] else '')

    @property
    def linestyle(self):
        """Iterates through each row and returns a list of linestyle combobox selections."""

        return [combo.get() for combo in self.linestyle_combos]

    @linestyle.setter
    def linestyle(self, linestyles):
        """Sets the value of each linestyle combobox with the appropriate value."""

        if linestyles:
            for i in range(len(linestyles)):
                self.linestyle_choices[i].set(linestyles[i] if linestyles[i] else '')

    @property
    def plus_tolerance(self):
        """Iterates through each row and returns a list of plus tolerance inputs."""

        return [entry.get() for entry in self.plus_tolerance_entries]

    @plus_tolerance.setter
    def plus_tolerance(self, tolerances):
        """Sets the value of each plus tolerance entry with the appropriate value."""

        if tolerances:
            for i in range(len(tolerances)):
                self.plus_tolerance_entries[i].delete(0, 'end')
                self.plus_tolerance_entries[i].insert(0, tolerances[i] if tolerances[i] else '')

    @property
    def minus_tolerance(self):
        """Iterates through each row and returns a list of minus tolerance inputs."""

        return [entry.get() for entry in self.minus_tolerance_entries]

    @minus_tolerance.setter
    def minus_tolerance(self, tolerances):
        """Sets the value of each minus tolerance entry with the appropriate value."""

        if tolerances:
            for i in range(len(tolerances)):
                self.minus_tolerance_entries[i].delete(0, 'end')
                self.minus_tolerance_entries[i].insert(0, tolerances[i] if tolerances[i] else '')

    @property
    def lag(self):
        """Iterates through each row and returns a list of lag inputs."""

        return [entry.get() for entry in self.lag_entries]

    @lag.setter
    def lag(self, lags):
        """Sets the value of each lag entry with the appropriate value."""

        if lags:
            for i in range(len(lags)):
                self.lag_entries[i].delete(0, 'end')
                self.lag_entries[i].insert(0, lags[i] if lags[i] else '')

    @property
    def bands_plus(self):
        """Gets the plus band data."""

        return self.plus_bands

    @bands_plus.setter
    def bands_plus(self, bands):
        """Sets the plus band data."""

        self.plus_bands = bands


    @property
    def bands_minus(self):
        """Gets the minus band data."""

        return self.minus_bands

    @bands_minus.setter
    def bands_minus(self, bands):
        """Sets the minus band data."""

        self.minus_bands = bands


class LimitLines(tk.Frame):
    """Creates a GUI frame that can hold a dynamic amount of rows for
    horizontal line fields. Keeps track of inputs."""

    def __init__(self):
        """Initialize the object's attributes."""

        # Initialize/reset the object's attributes
        self.reset()

    def setup(self, master):
        """Create the toolbar of the Tolerance Bands object. This function is called
        every time the page is flipped."""

        # Initialize the Limit Lines object as a frame
        tk.Frame.__init__(self, master=master)
        self.columnconfigure(0, weight=1)

        # Create a controls frame, which will function as a toolbar
        controls = tk.Frame(self)
        controls.grid(row=0, column=0, sticky='NSEW')
        controls.columnconfigure(0, weight=1)

        # Add the title of the section
        title = tk.Label(controls, text='Limit Lines',
                         font=('TkDefaultFont', 10, 'bold'))
        title.grid(row=0, column=0, sticky='W')

        # Add a button that adds another row to the object
        add_button = ttk.Button(controls, text='+', width=3, takefocus=0,
                                command=self.add_line)
        add_button.grid(row=0, column=1)

        # Add a button that deletes a row from the object
        delete_button = ttk.Button(controls, text='-', width=3, takefocus=0,
                                   command=self.delete_line)
        delete_button.grid(row=0, column=2)

    def reset(self):
        """Reset the attributes of the object to their default states. Called
        whenever a Tolerance Bands object is created or recreated."""

        # Reset the row count to 0
        self.count = 0
        # Reset the bands list, which holds a reference to each row
        self.lines = []
        # Reset the choices list for the comboboxes
        self.axis_choices = []
        self.orientation_choices = []
        self.color_choices = []
        self.linestyle_choices = []
        # Reset the lists that hold references to each field of each row
        self.axis_combos = []
        self.orientation_combos = []
        self.value_entries = []
        self.color_combos = []
        self.linestyle_combos = []
        self.alpha_entries = []

    def recreate(self, rows):
        """Recreates the rows that were previously in the Limit Lines object
        before the page was flipped. The rows parameter is calculated outside of
        the purview of this object and then passed in."""

        # Reset the object's attribute
        self.reset()
        # Add as many rows as there were before the page was flipped
        for row in range(rows):
            self.add_line(recreate=row)

    def add_line(self, recreate=None):
        """Add a row to the Limit Lines object."""

        # Define the general amount of padding to use between widgets
        PADDING = 2
        COMBO_WIDTH = 14
        ENTRY_WIDTH = 16

        # Create a labelframe that will hold all of the fields
        frame = tk.LabelFrame(self)
        frame.grid(row=self.count+1 if not recreate else recreate+1,
                   column=0, pady=(10, 0))

        # Create a frame insnide of the labelframe with padding
        container = tk.Frame(frame)
        container.grid(row=0, column=0, padx=10, pady=10, sticky='NSEW')

        # Add labels for axis, orientation, value, color, linestyle, and alpha
        axis_label = ttk.Label(container, text='axis:')
        axis_label.grid(row=0, column=0, padx=PADDING)
        orientation_label = ttk.Label(container, text='orientation:')
        orientation_label.grid(row=0, column=1, padx=PADDING)

        value_label = ttk.Label(container, text='value:')
        value_label.grid(row=0, column=2, padx=PADDING)

        color_label = ttk.Label(container, text='color:')
        color_label.grid(row=2, column=0, padx=PADDING)

        linestyle_label = ttk.Label(container, text='linestyle:')
        linestyle_label.grid(row=2, column=1, padx=PADDING)

        alpha_label = ttk.Label(container, text='alpha:')
        alpha_label.grid(row=2, column=2, padx=PADDING)

        # Add a combobox to select which axis to plot the line on
        axis_choice = tk.StringVar()
        axis_choice.set('primary')
        axis_combo = ttk.Combobox(container, width=COMBO_WIDTH, state='readonly',
                                    textvariable=axis_choice,
                                    values=['primary', 'secondary'])
        axis_combo.grid(row=1, column=0, padx=PADDING)
        self.axis_choices.append(axis_choice)
        self.axis_combos.append(axis_combo)

        # Add a combobox to select which way to orient the line
        orientation_choice = tk.StringVar()
        orientation_choice.set('horizontal')
        orientation_combo = ttk.Combobox(container, width=COMBO_WIDTH, state='readonly',
                                    textvariable=orientation_choice,
                                    values=['vertical', 'horizontal'])
        orientation_combo.grid(row=1, column=1, padx=PADDING)
        self.orientation_choices.append(orientation_choice)
        self.orientation_combos.append(orientation_combo)

        # Add an entry where the user can specify the appropriate coordinate/value
        value_entry = ttk.Entry(container, width=ENTRY_WIDTH, justify='center')
        value_entry.grid(row=1, column=2, padx=PADDING)
        self.value_entries.append(value_entry)

        # Add a combobox to select which color the line should be
        color_choice = tk.StringVar()
        color_choice.set(random.choice(list(app.plot_colors.keys())))
        color_combo = ttk.Combobox(container, textvariable=color_choice,
                                   width=COMBO_WIDTH, state='readonly')
        color_combo['values'] = list(app.plot_colors.keys())
        color_combo.grid(row=3, column=0, padx=PADDING)
        self.color_choices.append(color_choice)
        self.color_combos.append(color_combo)

        # Add a combobox to select which linestyle to use for the plot
        linestyle_choice = tk.StringVar()
        linestyle_choice.set('solid')
        linestyle_combo = ttk.Combobox(container, width=COMBO_WIDTH, state='readonly',
                                    textvariable=linestyle_choice,
                                    values=['solid', 'dotted', 'dashed', 'dashdot'])
        linestyle_combo.grid(row=3, column=1, padx=PADDING)
        self.linestyle_choices.append(linestyle_choice)
        self.linestyle_combos.append(linestyle_combo)

        # Add an entry where the user can specify alpha
        alpha_entry = ttk.Entry(container, width=ENTRY_WIDTH, justify='center')
        alpha_entry.grid(row=3, column=2, padx=PADDING)
        self.alpha_entries.append(alpha_entry)

        # Add one to the row count and keep a reference to this row
        self.count += 1
        self.lines.append(frame)

    def delete_line(self):
        """Remove a row from the Tolerance Bands object."""

        # If there are already no rows, exit the method
        if len(self.lines) == 0: return

        # Destroy the last row and remove all references to the objects
        self.lines[-1].destroy()
        del(self.lines[-1])
        del(self.orientation_choices[-1])
        del(self.orientation_combos[-1])
        del(self.linestyle_choices[-1])
        del(self.linestyle_combos[-1])
        del(self.axis_choices[-1])
        del(self.axis_combos[-1])
        del(self.value_entries[-1])
        del(self.color_choices[-1])
        del(self.color_combos[-1])
        del(self.alpha_entries[-1])
        # Decrease the row count by one
        self.count -= 1

    @property
    def axis(self):
        """Iterates through each row and returns a list of axis combobox selections."""

        return [combo.get() for combo in self.axis_combos]

    @axis.setter
    def axis(self, axis):
        """Sets the value of each axis combobox with the appropriate value."""

        if axis:
            for i in range(len(axis)):
                self.axis_choices[i].set(axis[i] if axis[i] else '')

    @property
    def orientation(self):
        """Iterates through each row and returns a list of orientation combobox selections."""

        return [combo.get() for combo in self.orientation_combos]

    @orientation.setter
    def orientation(self, orientation):
        """Sets the value of each orientation combobox with the appropriate value."""

        if orientation:
            for i in range(len(orientation)):
                self.orientation_choices[i].set(orientation[i] if orientation[i] else '')

    @property
    def value(self):
        """Iterates through each row and returns a list of minus tolerance inputs."""

        return [entry.get() for entry in self.value_entries]

    @value.setter
    def value(self, value):
        """Sets the value of each minus tolerance entry with the appropriate value."""

        if value:
            for i in range(len(value)):
                self.value_entries[i].delete(0, 'end')
                self.value_entries[i].insert(0, value[i] if value[i] else '')

    @property
    def color(self):
        """Iterates through each row and returns a list of color combobox selections."""

        return [combo.get() for combo in self.color_combos]

    @color.setter
    def color(self, colors):
        """Sets the value of each color combobox with the appropriate value."""

        if colors:
            for i in range(len(colors)):
                self.color_choices[i].set(colors[i] if colors[i] else '')

    @property
    def linestyle(self):
        """Iterates through each row and returns a list of linestyle selections."""

        return [combo.get() for combo in self.linestyle_combos]

    @linestyle.setter
    def linestyle(self, linestyles):
        """Sets the value of each linestyle combo with the appropriate value."""

        if linestyles:
            for i in range(len(linestyles)):
                self.linestyle_combos[i].set(linestyles[i] if linestyles[i] else '')

    @property
    def alpha(self):
        """Iterates through each row and returns a list of alpha inputs."""

        return [entry.get() for entry in self.alpha_entries]

    @alpha.setter
    def alpha(self, alphas):
        """Sets the value of each alpha entry with the appropriate value."""

        if alphas:
            for i in range(len(alphas)):
                self.alpha_entries[i].delete(0, 'end')
                self.alpha_entries[i].insert(0, alphas[i] if alphas[i] else '')


class Help(tk.Toplevel):
    """Help window that displays useful information such as button information
    and keyboard shortcuts to the user."""

    def __init__(self, *args, **kwargs):
        """Create the help window."""

        def on_close():
            """Define what happens when the help window is closed."""

            # Destroy the window and reset the help window tracker variable
            self.destroy()
            app.HELP = False

        MARGIN = 12
        CANVAS_WIDTH = 375
        CANVAS_HEIGHT = 400
        VERDANA = ('Verdana', 10, 'bold')
        HELVETICA = ('Helvetica', 10, 'bold')

        tk.Toplevel.__init__(self, *args, **kwargs)

        self.title('Help')
        self.resizable(width=False, height=False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", on_close)

        help_book = ttk.Notebook(self)
        help_book.grid(row=0, column=0, padx=MARGIN, pady=MARGIN, sticky='NSEW')

        # Inputs tab
        inputs = gui.ScrollableTab(help_book, 'Inputs', cheight=400, cwidth=375)

        input_labels = [
                    'Data start rows',
                    'Label rows',
                    'Unit rows [optional]',
                    'x column',
                    'y1 columns [multiple inputs]',
                    'y2 columns [optional] [multiple inputs]',
                    'Title [optional]',
                    'x axis label [optional]',
                    'y1 axis label [optional]',
                    'y2 axis label [optional]',
                    'Other',
                   ]

        input_text = [
                       'The row number that the data starts on.',
                       'The row number that the series labels are found on.',
                       'The row number that the units are found on.',
                       'The column that you want to plot on the x-axis.',
                       'The column(s) that you want to plot on the primary y-axis.',
                       'The column(s) that you want to plot on the secondary y-axis.',
                       'Overwrites the pregenerated title.',
                       'Overwrites the pregenerated x-axis label.',
                       'Overwrites the pregenerated primary y-axis label.',
                       'Overwrites the pregenerated secondary y-axis label.',
                       'In a field where multiple inputs are allowed ' \
                            '(i.e. \'y1 columns\' and \'y2 columns\'), ' \
                            'separate the inputs with any non-numeric character(s).\n' \
                       '\nFor example, \'1;3;5;7\' and \'1abc3.5 7\' will successfully ' \
                            'plot columns 1, 3, 5, and 7, but \'1357\' or \'1133577\' will not.'
                     ]

        help_row = 0

        for i, INPUT in enumerate(input_text):
            inputs.grid_rowconfigure(help_row, minsize=MARGIN)
            help_row += 1

            title = tk.Label(inputs, text=input_labels[i], wraplength=345,
                font=('Helvetica', 8, 'bold'))
            title.grid(row=help_row, column=0, padx=10, sticky="W")
            help_row += 1

            inputs.grid_rowconfigure(help_row, minsize=MARGIN/2)
            help_row += 1

            label = tk.Label(inputs, text=INPUT, wraplength=345)
            label.grid(row=help_row, column=0, padx=10, sticky="W")
            help_row += 1

            inputs.grid_rowconfigure(help_row, minsize=MARGIN)
            help_row += 1

            if INPUT != input_text[-1]:
                separation = tk.Frame(inputs)
                ttk.Separator(separation, orient='horizontal').grid(row=1, column=0, sticky="EW")
                separation.columnconfigure(0, weight=1)
                separation.grid(row=help_row, column=0, sticky="EW")
                help_row += 1

        # Controls tab
        controls = gui.ScrollableTab(help_book, 'Controls', cheight=400, cwidth=375)
        controls_row = 0

        plus_frame = tk.Frame(controls)
        plus_image = gui.RenderImage('Assets\\plus.png', downscale=5)
        plus_label = ttk.Button(plus_frame, takefocus=0, image=plus_image)
        plus_label.image = plus_image
        plus_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="EW")
        plus_separator = gui.Separator(plus_frame, orientation='vertical',
            padding=((0, 10), 0))
        plus_separator.grid(row=0, column=1, rowspan=2, sticky='NS')
        plus_title = ttk.Label(plus_frame, text='Create Row', font=HELVETICA)
        plus_title.grid(row=0, column=2, sticky='EW')
        plus_description = ttk.Label(plus_frame,
            text='Creates a row at the bottom of the selected file.')
        plus_description.grid(row=1, column=2, sticky='EW')
        plus_frame.grid(row=controls_row, column=0, padx=MARGIN, pady=MARGIN, sticky='NSEW')
        controls_row += 1

        minus_frame = tk.Frame(controls)
        minus_image = gui.RenderImage('Assets\\minus.png', downscale=5)
        minus_label = ttk.Button(minus_frame, takefocus=0, image=minus_image)
        minus_label.image = minus_image
        minus_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="EW")
        minus_separator = gui.Separator(minus_frame, orientation='vertical',
            padding=((0, 10), 0))
        minus_separator.grid(row=0, column=1, rowspan=2, sticky='NS')
        minus_title = ttk.Label(minus_frame, text='Delete Row', font=HELVETICA)
        minus_title.grid(row=0, column=2, sticky='EW')
        minus_description = ttk.Label(minus_frame,
            text='Deletes the bottom row of the selected file.')
        minus_description.grid(row=1, column=2, sticky='EW')
        minus_frame.grid(row=controls_row, column=0, padx=MARGIN, pady=MARGIN, sticky='NSEW')
        controls_row += 1

        copy_frame = tk.Frame(controls)
        copy_image = gui.RenderImage('Assets\\copy.png', downscale=5)
        copy_label = ttk.Button(copy_frame, takefocus=0, image=copy_image)
        copy_label.image = copy_image
        copy_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="EW")
        copy_separator = gui.Separator(copy_frame, orientation='vertical',
            padding=((0, 10), 0))
        copy_separator.grid(row=0, column=1, rowspan=2, sticky='NS')
        copy_title = ttk.Label(copy_frame, text='Copy', font=HELVETICA)
        copy_title.grid(row=0, column=2, sticky='EW')
        copy_description = ttk.Label(copy_frame,
            text='Copy data from the respective fields.')
        copy_description.grid(row=1, column=2, sticky='EW')
        copy_frame.grid(row=controls_row, column=0, padx=MARGIN, pady=MARGIN, sticky='NSEW')
        controls_row += 1

        paste_frame = tk.Frame(controls)
        paste_image = gui.RenderImage('Assets\\paste.png', downscale=5)
        paste_label = ttk.Button(paste_frame, takefocus=0, image=paste_image)
        paste_label.image = paste_image
        paste_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="EW")
        paste_separator = gui.Separator(paste_frame, orientation='vertical',
            padding=((0, 10), 0))
        paste_separator.grid(row=0, column=1, rowspan=2, sticky='NS')
        paste_title = ttk.Label(paste_frame, text='Paste', font=HELVETICA)
        paste_title.grid(row=0, column=2, sticky='EW')
        paste_description = ttk.Label(paste_frame,
            text='Pastes data into the respective fields.')
        paste_description.grid(row=1, column=2, sticky='EW')
        paste_frame.grid(row=controls_row, column=0, padx=MARGIN, pady=MARGIN, sticky='NSEW')
        controls_row += 1

        clear_frame = tk.Frame(controls)
        clear_image = gui.RenderImage('Assets\\clear.png', downscale=5)
        clear_label = ttk.Button(clear_frame, takefocus=0, image=clear_image)
        clear_label.image = clear_image
        clear_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="EW")
        clear_separator = gui.Separator(clear_frame, orientation='vertical',
            padding=((0, 10), 0))
        clear_separator.grid(row=0, column=1, rowspan=2, sticky='NS')
        clear_title = ttk.Label(clear_frame, text='Clear', font=HELVETICA)
        clear_title.grid(row=0, column=2, sticky='EW')
        clear_description = ttk.Label(clear_frame,
            text='Clear data from the respective fields.')
        clear_description.grid(row=1, column=2, sticky='EW')
        clear_frame.grid(row=controls_row, column=0, padx=MARGIN, pady=MARGIN, sticky='NSEW')
        controls_row += 1

        edit_menu_frame = tk.Frame(controls)

        label_frame = tk.Frame(edit_menu_frame)
        menu1_label = ttk.Label(label_frame, text='Edit', anchor='center', font=HELVETICA)
        menu1_label.grid(row=1, column=0, sticky='NSEW')
        menu2_label = ttk.Label(label_frame, text='Menu', anchor='center', font=HELVETICA)
        menu2_label.grid(row=2, column=0, sticky='NSEW')
        label_frame.grid_rowconfigure(0, weight=1)
        label_frame.grid_rowconfigure(3, weight=1)
        label_frame.grid(row=0, column=0, padx=(6, 15), sticky='NSEW')

        edit_menu_separator = gui.Separator(edit_menu_frame, orientation='vertical',
            padding=((0, 10), 0))
        edit_menu_separator.grid(row=0, column=1, sticky='NS')

        descriptions_frame = tk.Frame(edit_menu_frame)

        clear_form_frame = tk.Frame(descriptions_frame)
        clear_form_title = ttk.Label(clear_form_frame, text='Edit > Clear Form',
            font=HELVETICA)
        clear_form_title.grid(row=0, column=2, sticky='EW')
        clear_form_description = ttk.Label(clear_form_frame,
            text='Clear data from all fields.')
        clear_form_description.grid(row=1, column=2, sticky='EW')
        clear_form_frame.grid(row=0, column=0, pady=(0, MARGIN/2), sticky='NSEW')

        reset_frame = tk.Frame(descriptions_frame)
        reset_title = ttk.Label(reset_frame, text='Edit > Reset Form',
            font=HELVETICA)
        reset_title.grid(row=0, column=2, sticky='EW')
        reset_description = ttk.Label(reset_frame,
            text='Clear inputs and revert form back to its original state.')
        reset_description.grid(row=1, column=2, sticky='EW')
        reset_frame.grid(row=1, column=0, pady=MARGIN/2, sticky='NSEW')

        paste_one_frame = tk.Frame(descriptions_frame)
        paste_one_title = ttk.Label(paste_one_frame, text='Edit > Paste (Selected File)',
            font=HELVETICA)
        paste_one_title.grid(row=0, column=2, sticky='EW')
        paste_one_description = ttk.Label(paste_one_frame,
            text='Pastes contents of the clipboard into all fields of the\nselected file.')
        paste_one_description.grid(row=1, column=2, sticky='EW')
        paste_one_frame.grid(row=2, column=0, pady=MARGIN/2, sticky='NSEW')

        paste_all_frame = tk.Frame(descriptions_frame)
        paste_all_title = ttk.Label(paste_all_frame, text='Edit > Paste (All Files)',
            font=HELVETICA)
        paste_all_title.grid(row=0, column=2, sticky='EW')
        paste_all_description = ttk.Label(paste_all_frame,
            text='Pastes contents of the clipboard into all fields of all\nfiles.')
        paste_all_description.grid(row=1, column=2, sticky='EW')
        paste_all_frame.grid(row=3, column=0, pady=(MARGIN/2, 0), sticky='NSEW')

        descriptions_frame.grid(row=0, column=2, sticky='NSEW')

        edit_menu_frame.grid(row=controls_row, column=0, padx=MARGIN, pady=MARGIN, sticky='NSEW')

        # Shortcuts tab
        shortcuts = gui.ScrollableTab(help_book, 'Shortcuts', cheight=400, cwidth=375)
        shortcuts_row = 0

        COLUMN_SIZE = 110
        ROW_SIZE = 30

        enter_frame = tk.Frame(shortcuts, pady=MARGIN)
        enter_frame.grid(row=shortcuts_row, column=0, sticky='NSEW')
        enter_frame.columnconfigure(0, minsize=COLUMN_SIZE)
        enter_frame.rowconfigure(0, minsize=ROW_SIZE)
        enter_frame.rowconfigure(1, minsize=ROW_SIZE)
        enter_label = ttk.Label(enter_frame, text='<Enter>', anchor='center',
            font=VERDANA)
        enter_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), sticky='NSEW')
        enter_separator = gui.Separator(enter_frame, orientation='vertical',
            padding=((0, 10), 0))
        enter_separator.grid(row=0, column=1, rowspan=2, sticky='NSEW')
        enter_title = ttk.Label(enter_frame, text='Keypress: Enter',
            font=HELVETICA)
        enter_title.grid(row=0, column=2, sticky='EW')
        enter_description = ttk.Label(enter_frame,
            text='Bound to the [Plot] button.\nTakes the user\'s inputs and plots the data.')
        enter_description.grid(row=1, column=2, sticky='EW')
        shortcuts_row += 1

        create_row_frame = tk.Frame(shortcuts, pady=MARGIN)
        create_row_frame.grid(row=shortcuts_row, column=0, sticky='NSEW')
        create_row_frame.columnconfigure(0, minsize=COLUMN_SIZE)
        create_row_frame.rowconfigure(0, minsize=ROW_SIZE)
        create_row_frame.rowconfigure(1, minsize=ROW_SIZE)
        create_row_label = ttk.Label(create_row_frame, text='<Ctrl>\n+ <+>', anchor='center',
            font=VERDANA)
        create_row_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), sticky='NSEW')
        create_row_separator = gui.Separator(create_row_frame, orientation='vertical',
            padding=((0, 10), 0))
        create_row_separator.grid(row=0, column=1, rowspan=2, sticky='NSEW')
        create_row_title = ttk.Label(create_row_frame, text='Combination: Control + Plus',
            font=HELVETICA)
        create_row_title.grid(row=0, column=2, sticky='EW')
        create_row_description = ttk.Label(create_row_frame,
            text='Bound to the [+] button.\nCreates a new row in the selected tab.')
        create_row_description.grid(row=1, column=2, sticky='EW')
        shortcuts_row += 1

        delete_row_frame = tk.Frame(shortcuts, pady=MARGIN)
        delete_row_frame.grid(row=shortcuts_row, column=0, sticky='NSEW')
        delete_row_frame.columnconfigure(0, minsize=COLUMN_SIZE)
        delete_row_frame.rowconfigure(0, minsize=ROW_SIZE)
        delete_row_frame.rowconfigure(1, minsize=ROW_SIZE)
        delete_row_label = ttk.Label(delete_row_frame, text='<Ctrl>\n+ <->', anchor='center',
            font=VERDANA)
        delete_row_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), sticky='NSEW')
        delete_row_separator = gui.Separator(delete_row_frame, orientation='vertical',
            padding=((0, 10), 0))
        delete_row_separator.grid(row=0, column=1, rowspan=2, sticky='NSEW')
        delete_row_title = ttk.Label(delete_row_frame, text='Combination: Control + Minus',
            font=HELVETICA)
        delete_row_title.grid(row=0, column=2, sticky='EW')
        delete_row_description = ttk.Label(delete_row_frame,
            text='Bound to the [-] button.\nDeletes the bottom row of the selected tab.')
        delete_row_description.grid(row=1, column=2, sticky='EW')
        shortcuts_row += 1

        insert_frame = tk.Frame(shortcuts, pady=MARGIN)
        insert_frame.grid(row=shortcuts_row, column=0, sticky='NSEW')
        insert_frame.columnconfigure(0, minsize=COLUMN_SIZE)
        insert_frame.rowconfigure(0, minsize=ROW_SIZE)
        insert_frame.rowconfigure(1, minsize=ROW_SIZE)
        insert_label = ttk.Label(insert_frame, text='<Insert>', anchor='center',
            font=VERDANA)
        insert_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), sticky='NSEW')
        insert_separator = gui.Separator(insert_frame, orientation='vertical',
            padding=((0, 10), 0))
        insert_separator.grid(row=0, column=1, rowspan=2, sticky='NSEW')
        insert_title = ttk.Label(insert_frame, text='Keypress: Insert',
            font=HELVETICA)
        insert_title.grid(row=0, column=2, sticky='EW')
        insert_description = ttk.Label(insert_frame,
            text='Selects the previous tab.')
        insert_description.grid(row=1, column=2, sticky='EW')
        shortcuts_row += 1

        page_up_frame = tk.Frame(shortcuts, pady=MARGIN)
        page_up_frame.grid(row=shortcuts_row, column=0, sticky='NSEW')
        page_up_frame.columnconfigure(0, minsize=COLUMN_SIZE)
        page_up_frame.rowconfigure(0, minsize=ROW_SIZE)
        page_up_frame.rowconfigure(1, minsize=ROW_SIZE)
        page_up_label = ttk.Label(page_up_frame, text='<PgUp>', anchor='center',
            font=VERDANA)
        page_up_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), sticky='NSEW')
        page_up_separator = gui.Separator(page_up_frame, orientation='vertical',
            padding=((0, 10), 0))
        page_up_separator.grid(row=0, column=1, rowspan=2, sticky='NSEW')
        page_up_title = ttk.Label(page_up_frame, text='Keypress: Page Up',
            font=HELVETICA)
        page_up_title.grid(row=0, column=2, sticky='EW')
        page_up_description = ttk.Label(page_up_frame,
            text='Selects the next tab.')
        page_up_description.grid(row=1, column=2, sticky='EW')
        shortcuts_row += 1

        previous_row_frame = tk.Frame(shortcuts, pady=MARGIN)
        previous_row_frame.grid(row=shortcuts_row, column=0, sticky='NSEW')
        previous_row_frame.columnconfigure(0, minsize=COLUMN_SIZE)
        previous_row_frame.rowconfigure(0, minsize=ROW_SIZE)
        previous_row_frame.rowconfigure(1, minsize=ROW_SIZE)
        previous_row_label = ttk.Label(previous_row_frame, text='  <Ctrl>\n+ <Shift>\n + <Tab>',
            anchor='center', font=VERDANA)
        previous_row_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), sticky='NSEW')
        previous_row_separator = gui.Separator(previous_row_frame, orientation='vertical',
            padding=((0, 10), 0))
        previous_row_separator.grid(row=0, column=1, rowspan=2, sticky='NSEW')
        previous_row_title = ttk.Label(previous_row_frame,
            text='Combination: Control + Shift + Tab ', font=HELVETICA)
        previous_row_title.grid(row=0, column=2, sticky='EW')
        previous_row_description = ttk.Label(previous_row_frame,
            text='Selects the currently selected field of the\nprevious row.')
        previous_row_description.grid(row=1, column=2, sticky='EW')
        shortcuts_row += 1

        next_row_frame = tk.Frame(shortcuts, pady=MARGIN)
        next_row_frame.grid(row=shortcuts_row, column=0, sticky='NSEW')
        next_row_frame.columnconfigure(0, minsize=COLUMN_SIZE)
        next_row_frame.rowconfigure(0, minsize=ROW_SIZE)
        next_row_frame.rowconfigure(1, minsize=ROW_SIZE)
        next_row_label = ttk.Label(next_row_frame, text='  <Ctrl>\n+ <Tab>',
            anchor='center', font=VERDANA)
        next_row_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), sticky='NSEW')
        next_row_separator = gui.Separator(next_row_frame, orientation='vertical',
            padding=((0, 10), 0))
        next_row_separator.grid(row=0, column=1, rowspan=2, sticky='NSEW')
        next_row_title = ttk.Label(next_row_frame,
            text='Combination: Control + Tab ', font=HELVETICA)
        next_row_title.grid(row=0, column=2, sticky='EW')
        next_row_description = ttk.Label(next_row_frame,
            text='Selects the currently selected field of the\nnext row.')
        next_row_description.grid(row=1, column=2, sticky='EW')

        gui.CenterWindow(self)


# Initialize the application
app = Application()
# Run a test function
app.after(100, app.test)
# Run the program in a continuous loop
app.mainloop()