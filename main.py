# GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from tkinter import filedialog as fd
from tkinter import messagebox as msg
from PIL import Image, ImageTk
from lemons import gui

# System packages
import os
import platform

# Plotting packages
import matplotlib as mpl
if platform.system() == 'Darwin':
    mpl.use("TkAgg") # On Mac, this must come before the pyplot import
import matplotlib.pyplot as plt
if platform.system() == 'Windows':
    mpl.use("TkAgg") # On Windows, this must come after the pyplot import
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

# Import custom classes for each type of file
from basic import BasicFile, BasicControls
from peakvalley import PeakValleyFile, PeakValleyControls


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
        filetypes = [
            ('Comma-Separated Values (*.csv)', '*.csv'),
            ('Excel Spreadsheet (*.xls)', '*.xls'),
            ('Excel Spreadsheet (*.xlsx)', '*.xlsx'),
            ('Data File (*.dat)', '*.dat')
        ]
        browse_image = gui.RenderImage('Assets\\browse.png', downscale=9)
        self.listbox = gui.InputField(self, quantity='multiple', appearance='list', width=80,
                                 image=browse_image, command=self.browse, filetypes=filetypes)
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
        # default_binding = self.root.bind('<Return>', self.open_flipbook)

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
            
            # Special files are currently unsupported, so skip them
            if isinstance(file, PeakValleyFile): continue

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

        # 
        LOAD_ERROR = False

        # If no location was specified, have the user navigate to the preset file
        if not location:
            filetypes = [('Configuration Files (*.ini)', '*.ini')]
            location = fd.askopenfilename(title='Choose the preset file',
                                          filetypes=filetypes)

        # Initialize a ConfigObj object
        preset = configobj.ConfigObj(location)

        # If the user presses cancel or if the preset file is empty (possibly corrupt),
        # display a message and exit the function.
        if len(preset) == 0:
            # message = 'It looks like the preset file you chose is either empty or not ' \
            #           'formatted correctly. Please double check the file and try again.'
            # msg.showinfo('Oops!', message)
            return

        # inputs = [(i, info['type'], info['filepath']) for i, info in enumerate(preset.values()) \
        #           if os.path.isfile(info['filepath'])]
        inputs = [(key, info['type'], info['filepath']) for key, info in preset.items() \
                  if os.path.isfile(info['filepath'])]
        if not inputs:
            message = 'There are no valid filepaths in this preset. Please verify that ' \
                      'they are correct, and that the files still exist, and try again.'
            msg.showinfo('Oops!', message)
            return
        if len(inputs) != len(preset.keys()):
            LOAD_ERROR = True
        keys = [key for key, _, _ in inputs]
        types = [filetype for _, filetype, _ in inputs]
        self.inputs = [filepath for _, _, filepath in inputs]

        # Insert the filepaths into the listbox
        self.listbox.clear()
        self.listbox.field['state'] = 'normal'
        for filepath in self.inputs:
            self.listbox.field.insert('end', ' ' + filepath)
        self.listbox.field['state'] = 'disable'
        self.listbox.field['justify'] = 'left'

        # With the inputs variable initialized, it is safe to enable all fields and
        # create tabs/rows for each input
        self.enable()

        # Destroy everything in the primary frame
        for child in self.primary.winfo_children(): child.destroy()

        # Place a notebook in the primary frame
        self.notebook = ttk.Notebook(self.primary, takefocus=0)
        self.notebook.grid(row=0, column=0, sticky='NSEW')

        # Initialize the files attribute
        # backup = self.files.copy() if hasattr(self, 'files') else []
        self.files = []

        # Create the appropriate type of file and append it to self.files
        for i, item in enumerate(types):
            if item == 'Basic':
                file = BasicFile(self.notebook, self.inputs[i], self)
            elif item == 'Peak Valley':
                file = PeakValleyFile(self.notebook, self.inputs[i], self)
            else:
                # self.files = backup.copy()
                self.reset()
                message = 'One or more of the files in the selected preset' \
                          ' have an invalid type.\n\nValid types:\n - Basic\n' \
                          ' - Peak Valley\n\nPlease check and try again.'
                msg.showinfo('Invalid type', message)
                return # requires a more thought-out approach
            self.files.append(file)

        # The number of items in each section of the preset that are not plot subsections
        header = {
            'Basic': 5,
            'Peak Valley': 8,
        }

        # Grab the relevant info and pass it to the file's load_preset method
        for i, file in enumerate(self.files):
            # Add the appropriate number of rows to each tab/file
            number_of_plots = len(preset[keys[i]]) - header[types[i]]
            rows_needed = ( number_of_plots - 1 ) if number_of_plots > 0 else 0
            # Pass the relevant information to the file's load_preset method
            info = preset[keys[i]]
            file.load_preset(self, i, rows_needed, info)

        # If a file could not be found, display a message
        if LOAD_ERROR:
            message = 'Unable to find one or more of the files in the preset.' \
                      ' Please check that the filepaths are correct.' \
                      ' Otherwise, the remaining files have been loaded' \
                      ' successfully.'
            msg.showinfo('Load preset error', message)


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
        self.file_menu.entryconfig(3, state='normal')
        self.file_menu.entryconfig(5, state='normal')

        # Enable the entries in the edit menu
        self.edit_menu.entryconfig(0, state='normal')
        self.edit_menu.entryconfig(1, state='normal')
        self.edit_menu.entryconfig(3, state='normal')
        self.edit_menu.entryconfig(4, state='normal')


    def disable(self):
        """Change the GUI to its disabled state, which occurs when inputs are not loaded."""

        # Disable the buttons in the footer
        self.plot_button['state'] = 'disabled'
        self.plus_button['state'] = 'disabled'
        self.minus_button['state'] = 'disabled'

        # Disable the entries in the file menu
        self.file_menu.entryconfig(3, state='disabled')
        self.file_menu.entryconfig(5, state='disabled')

        # Disable the entries in the edit menu
        self.edit_menu.entryconfig(0, state='disabled')
        self.edit_menu.entryconfig(1, state='disabled')
        self.edit_menu.entryconfig(3, state='disabled')
        self.edit_menu.entryconfig(4, state='disabled')


    def reset(self):
        """Revert the GUI back to its disabled state, before any inputs were loaded."""

        # Clear the listbox
        self.listbox.clear()

        # Disable the GUI
        self.disable()

        # Destroy everything in the primary frame - namely, the notebook
        for child in self.primary.winfo_children(): child.destroy()

        # Reset the inputs and files lists
        self.inputs = []
        self.files = []

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
            self.files = [BasicFile(self.notebook, filepath, self) for filepath in self.inputs]
        elif special == 'Peak Valley':
            self.files = [PeakValleyFile(self.notebook, filepath, self) for filepath in self.inputs]

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
        if special == 'Peak Valley':
            filetypes = [
                ('Data File (*.dat)', '*.dat'),
                ('Comma-Separated Values (*.csv)', '*.csv')
            ]
        else:
            filetypes = [
                ('Comma-Separated values (*.csv)', '*.csv'),
                ('Excel Spreadsheet (*.xls)', '*.xls'),
                ('Excel Spreadsheet (*.xlsx)', '*.xlsx'),
                ('Data File (*.dat)', '*.dat')
            ]
        filepath = fd.askopenfilename(title='Choose the file',
                                      filetypes=filetypes)

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
            # # Place a notebook in the primary frame
            # self.notebook = ttk.Notebook(self.primary, takefocus=0)
            # self.notebook.grid(row=0, column=0, sticky='NSEW')
            # self.enable()
            # self.notebook.grid(row=0, column=0, sticky='NSEW')
            # Create a basic file object by default
            if not special:
                file = BasicFile(self.notebook, filepath, self)
            # Otherwise, if the user is adding a special file, create the
            # appropriate file object
            elif special == 'Peak Valley':
                file = PeakValleyFile(self.notebook, filepath, self)
            # Append it to the list of file objects
            self.files.append(file)
            # # Set cursor focus on the default field of the first tab for ease of use
            # self.files[0].set_default_focus()

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
        if not len(self.files) > 1:
            self.reset()
            return

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


    def validate_inputs(self):

        blanks = False
        length = False
        rows = False
        columns = False
        for file in self.files:
            status = file.validate_inputs()
            if status is True: continue
            elif status == 'blanks': blanks = True
            elif status == 'length': length = True
            elif status == 'rows': rows = True
            elif status == 'columns': columns = True
            file.reset()

        if any(item == True for item in [blanks, length, rows, columns]):

            title = 'Invalid input'
            message = ""
            count = [blanks, length, rows, columns].count(True)
            if count > 1:
                message += 'There were multiple problems with your input:\n'
            if blanks:
                if count == 1:
                    message += "It looks like you've left required fields" \
                                " blank."
                else:
                    message += " - Required field(s) left blank\n"
            if length:
                if count == 1:
                    message += "It looks like you\'ve entered more than one " \
                               "row or column in a field that cannot accept it."
                else:
                    message += " - Overloaded field(s)\n"
            if rows:
                if count == 1:
                    message += "It looks like you\'ve entered a row number in" \
                               " a field that is equal to or greater than the" \
                               " row you've entered in the corresponding " \
                               "'data start row' field."
                else:
                    message += " - Invalid row selection(s)\n"
            if columns:
                if count == 1:
                    message += "It looks like you've entered a column " \
                                "number that is out of range in one or " \
                                "more fields."
                else:
                    message += " - Invalid column selection(s)\n"
            message += '\nPlease correct and try again.'
            msg.showinfo(title, message)
            return False
        else:
            return True


    def open_flipbook(self, event=None):
        """Open the flipbook."""

        # If the flipbook is already open, exit the function
        if self.FLIPBOOK: return

        # Reset parameters to avoid problems associated with using styles
        mpl.rcParams.update(mpl.rcParamsDefault)

        # Check that the user's inputs are okay
        if not self.validate_inputs(): return

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
        Help(app.root)
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

        self.load_preset('Presets\\test.ini')
        # self.open_flipbook()


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

        # Create the controls button that allows the user to open the controls window
        controls_image = gui.RenderImage(gui.ResourcePath('Assets\\controls.png'), downscale=9)
        controls_button = ttk.Button(toolbar_frame, text='Controls', takefocus=0,
                                     image=controls_image, command=show_controls)
        controls_button.grid(row=0, column=1, sticky='E')
        controls_button.image = controls_image

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
        # self.canvas.mpl_connect('pick_event', self.on_click)
        self.figure.canvas.mpl_connect('pick_event', self.on_click)

        # Update the arrows and the plot of the flipbook
        self.update_arrows()
        self.update_plot()

        # If the controls window has not been created yet, create it and leave it hidden
        if not self.controls:
            # self.controls = Controls(self, self.plots[self.page])
            self.controls = Controls(self, self.page)
            self.controls.withdraw()

        # Make the flipbook visible again and center it on the screen
        self.deiconify()
        gui.CenterWindow(self)


    def update_plot(self):
        """Update the plot with new data or information."""

        current = self.plots[self.page] # Current plot object
        file_number = self.files[self.page] # File index
        plot_number = self.numbers[self.page] # Plot number in file

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
        # Add extra logic for the case of there only being two plots
        if self.pages == 1:
            if self.page == 0:
                self.previous_button.config(state='disabled')
                self.next_button.config(state='normal')
            elif self.page == 1:
                self.previous_button.config(state='normal')
                self.next_button.config(state='disabled')


    def flip_page(self, event, direction):
        """Flip between pages of the flipbook."""

        # Determine the destination page
        destination = (self.page + 1) if direction == 'right' else (self.page - 1)
        # If the destination page is within the range of the total number of pages...
        if destination in range(self.pages + 1):
            # Set the new page number; update arrows and the plot
            self.page += 1 if direction == 'right' else -1
            # self.controls.current = self.plots[self.page]
            self.controls.flip_page(self.page)
            self.update_plot()
            self.update_arrows()
            # Refresh the controls window
            self.controls.refresh()

        # Return 'break' to bypass event propagation
        return ('break')


    def on_click(self, event):
        """Hide or show a line when the corresponding object in the legend is clicked."""

        # Reroute to plot object's on_click method
        current = self.plots[self.page]
        current.on_click(event, self)

        # self.canvas.draw()

        # # Get a reference to the legend line and the original line
        # legend_line = event.artist
        # original_line = self.line_map[legend_line]
        # # Determine whether to show or hide the original line
        # visible = not original_line.get_visible()
        # # Set the visibility accordingly
        # original_line.set_visible(visible)
        # legend_line.set_alpha(1.0 if visible else 0.2)
        # # Update the plot
        # self.canvas.draw()


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

    def __init__(self, master, page):
        """Create a controls window where the user can adjust the plot."""

        # Create the top-level controls window
        tk.Toplevel.__init__(self, master)
        self.title('Controls')
        self.resizable(width=False, height=False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # When the user closes the controls window, just hide it instead
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

        # Initialize miscellaneous instance variables
        self.flipbook = master

        # Create the primary frame, which will hold the notebook and provide padding
        self.primary = gui.PaddedFrame(self)
        self.primary.grid(row=0, column=0, sticky='NSEW')
        self.primary.columnconfigure(0, weight=1)
        self.primary.rowconfigure(0, weight=1)

        # Initialize the notebook variable, which is the current page's controls
        self.notebook = None
        # Make a list of notebooks (one for each file) so that they can be
        # switched between instead of deleted and recreated upon a page change
        self.notebooks = []
        for file in self.flipbook.info:
            if isinstance(file, BasicFile):
                notebook = BasicControls(self.primary, takefocus=0)
            elif isinstance(file, PeakValleyFile):
                notebook = PeakValleyControls(self.primary, takefocus=0)
            self.notebooks.append(notebook)

        # self.page = page
        self.flip_page(page)

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
        self.bind('<Return>', self.update)


    def flip_page(self, page):
        """Upon changing this page of the flipbook, update instance attributes,
        remove the old controls from view, and show the controls of the current
        page.
        """

        # Set relevant attributes according to the page number
        self.page = page
        file_index = self.flipbook.files[page]
        self.file = self.flipbook.info[file_index]
        self.current = self.flipbook.plots[page]

        # If a notebook is already shown, remove it from view
        if self.notebook is not None:
            self.notebook.grid_forget()
            self.notebook = None

        # Show the new controls and update its attributes
        self.notebook = self.notebooks[file_index]
        self.notebook.grid(row=0, column=0, sticky='NSEW')
        self.notebook.current = self.current
        self.notebook.flipbook = self.flipbook


    def refresh(self):
        """Refresh the current page's controls/notebook."""

        self.notebook.refresh()


    def update(self, event=None):
        """Update the current page's controls/notebook."""

        self.notebook.update()


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