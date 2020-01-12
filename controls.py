import math
import random
import re
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk

import lemons.gui as gui
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from settings import plot_colors


class LabeledEntry(tk.Frame):

    def __init__(self, master, text, *args, **kwargs):

        tk.Frame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)

        label = tk.Label(self, text=text)
        label.grid(row=0, column=0, sticky='NSEW')

        self.entry = ttk.Entry(self)
        self.entry.grid(row=1, column=0, sticky='NSEW')

    def clear(self):
        original_state = self.entry['state']
        self.entry['state'] = 'normal'
        self.entry.delete(0, 'end')
        self.entry['state'] = original_state

    def get(self):
        return self.entry.get()

    def set(self, value):
        original_state = self.entry['state']
        self.entry['state'] = 'normal'
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)
        self.entry['state'] = original_state

    def __getitem__(self, item):
        return self.entry[item]
    
    def __setitem__(self, item, value):
        self.entry[item] = value


class LabeledCombobox(tk.Frame):

    def __init__(self, master, text, values, *args, **kwargs):

        tk.Frame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)

        label = tk.Label(self, text=text)
        label.grid(row=0, column=0, sticky='NSEW')

        self.combobox = ttk.Combobox(self, values=values, state='readonly')
        # self.combobox.set(values[0])
        self.combobox.grid(row=1, column=0, sticky='NSEW')

    def clear(self):
        original_state = self.combobox['state']
        self.combobox['state'] = 'normal'
        self.combobox.set('')
        self.combobox['state'] = original_state

    def get(self):
        return self.combobox.get()

    def set(self, value):
        # original_state = self.combobox['state']
        # self.combobox['state'] = 'normal'
        self.combobox.set(value)
        # self.combobox.set('Bold')
        # self.combobox['state'] = original_state

    def __getitem__(self, item):
        return self.combobox[item]
    
    def __setitem__(self, item, value):
        self.combobox[item] = value


class AxisLimits(tk.Frame):

    def __init__(self, *args, **kwargs):

        tk.Frame.__init__(self, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        # Define amount of padding to use around widgets
        PADDING = 10
        # Add the title of the section
        limits_title = tk.Label(self, text='Axis Limits',
                         font=('TkDefaultFont', 10, 'bold'))
        limits_title.grid(row=0, column=0, pady=(0, 10), sticky='W')
        # Create a lower x-axis label and entry
        self.x_lower_entry = LabeledEntry(self, 'x-lower:')
        self.x_lower_entry.grid(row=2, column=0, padx=PADDING, sticky='NSEW')
        # Create an upper x-axis label and entry
        self.x_upper_entry = LabeledEntry(self, 'x-upper:')
        self.x_upper_entry.grid(row=2, column=1, padx=PADDING, sticky='NSEW')
        # Add some vertical spacing between widgets
        gui.Space(self, row=3, column=0, columnspan=2)
        # Create a lower y1-axis label and entry
        self.y1_lower_entry = LabeledEntry(self, 'y1-lower:')
        self.y1_lower_entry.grid(row=5, column=0, padx=PADDING, sticky='NSEW')
        # Create an upper y1-axis label and entry
        self.y1_upper_entry = LabeledEntry(self, 'y1-upper:')
        self.y1_upper_entry.grid(row=5, column=1, padx=PADDING, sticky='NSEW')
        # Add some vertical spacing between widgets
        gui.Space(self, row=6, column=0, columnspan=2)
        # Create a lower y2-axis label and entry
        self.y2_lower_entry = LabeledEntry(self, 'y2_lower:')
        self.y2_lower_entry.grid(row=8, column=0, padx=PADDING, sticky='NSEW')
        # Create an upper y2-axis label and entry
        self.y2_upper_entry = LabeledEntry(self, 'y2_upper:')
        self.y2_upper_entry.grid(row=8, column=1, padx=PADDING, sticky='NSEW')

    @property
    def x_lower(self):
        return self.x_lower_entry.get()
    
    @x_lower.setter
    def x_lower(self, value):
        self.x_lower_entry.set(value[0] if value[0] else value[1])

    @property
    def x_upper(self):
        return self.x_upper_entry.get()
    
    @x_upper.setter
    def x_upper(self, value):
        self.x_upper_entry.set(value[0] if value[0] else value[1])

    @property
    def y1_lower(self):
        return self.y1_lower_entry.get()
    
    @y1_lower.setter
    def y1_lower(self, value):
        self.y1_lower_entry.set(value[0] if value[0] else value[1])

    @property
    def y1_upper(self):
        return self.y1_upper_entry.get()
    
    @y1_upper.setter
    def y1_upper(self, value):
        self.y1_upper_entry.set(value[0] if value[0] else value[1])

    @property
    def y2_lower(self):
        return self.y2_lower_entry.get()
    
    @y2_lower.setter
    def y2_lower(self, value):
        self.y2_lower_entry.set(value[0] if value[0] else value[1])

    @property
    def y2_upper(self):
        return self.y2_upper_entry.get()
    
    @y2_upper.setter
    def y2_upper(self, value):
        self.y2_upper_entry.set(value[0] if value[0] else value[1])


class AxisTicks(tk.Frame):

    def __init__(self, *args, **kwargs):

        tk.Frame.__init__(self, *args, **kwargs)

        # Define amount of padding to use around widgets
        PADDING = 10

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        # Add the title of the section
        ticks_title = tk.Label(self, text='Axis Ticks',
                         font=('TkDefaultFont', 10, 'bold'))
        ticks_title.grid(row=0, column=0, pady=(0, 10), sticky='W')
        # Create a label and an entry for the primary ticks
        self.primary_ticks_entry = LabeledEntry(self, 'Primary ticks:')
        self.primary_ticks_entry.grid(row=1, column=0, padx=PADDING, sticky='NSEW')
        # Create a label and an entry for the secondary ticks
        self.secondary_ticks_entry = LabeledEntry(self, 'Secondary ticks:')
        self.secondary_ticks_entry.grid(row=1, column=1, padx=PADDING, sticky='NSEW')

    @property
    def primary_ticks(self):
        return self.primary_ticks_entry.get()

    @primary_ticks.setter
    def primary_ticks(self, value):
        self.primary_ticks_entry.set(value[0] if value[0] else value[1])

    @property
    def secondary_ticks(self):
        return self.secondary_ticks_entry.get()

    @secondary_ticks.setter
    def secondary_ticks(self, value):
        self.secondary_ticks_entry.set(value[0] if value[0] else value[1])


class GeneralAppearance(tk.Frame):

    def __init__(self, master, *args, **kwargs):

        # The current plot object will be passed by the control's refresh method
        self.current = None

        tk.Frame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Add the title of the section
        general_title = tk.Label(self, text='General Appearance',
                         font=('TkDefaultFont', 10, 'bold'))
        general_title.grid(row=0, column=0, pady=(0, 10), columnspan=2, sticky='W')

        # Add a combobox to control the background of the plot
        self.background_choice = tk.StringVar()
        background_choices = ['None', 'Tactair', 'Young & Franklin', 'Custom']
        background_combo = LabeledCombobox(self, 'Background:', width=20,
                                           values=background_choices)
        background_combo['state'] = 'readonly'
        background_combo['textvariable'] = self.background_choice
        background_combo.grid(row=1, column=0, padx=10, sticky='NSEW')
        # background_combo.bind('<<ComboboxSelected>>', self._custom_background)
        background_combo.combobox.bind('<<ComboboxSelected>>', self._custom_background)

        # Add a combobox to control the style of the plot
        self.style_choice = tk.StringVar()
        style_choices = ['Default', 'Classic', 'Seaborn', 'Fivethirtyeight']
        style_combo = LabeledCombobox(self, 'Style:', values=style_choices,
                                      width=20)
        style_combo['state'] = 'readonly'
        style_combo['textvariable'] = self.style_choice
        style_combo.grid(row=1, column=1, padx=10, sticky='NSEW')
   
    def _custom_background(self, event=None):
        """Allow the user to navigate to and select a custom background.

        This function is called whenever an option in the appropriate combobox
        is selected. However, its purpose is to only execute when the 'Custom'
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

    @property
    def style(self):
        return self.style_choice.get()

    @style.setter
    def style(self, value):
        self.style_choice.set(value)

    @property
    def background(self):
        return self.background_choice.get()

    @background.setter
    def background(self, value):
        self.background_choice.set(value)


class LabelProperties(tk.Frame):

    def __init__(self, *args, **kwargs):

        tk.Frame.__init__(self, *args, **kwargs)
        self.columnconfigure(0, weight=1)

        # Add the title of the section
        general_title = tk.Label(self, text='Label Properties',
                                 font=('TkDefaultFont', 10, 'bold'))
        general_title.grid(row=0, column=0, pady=(0, 10), sticky='W')

        container = tk.Frame(self)
        container.grid(row=1, column=0, sticky='NSEW')
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # weights = ['Normal', 'Italics', 'Bold', 'Bold Italics']
        weights = ['Normal', 'Bold', 'Heavy', 'Light']

        self.title_weight_entry = LabeledCombobox(container, 'title weight:', values=weights)
        self.title_weight_entry.grid(row=0, column=0, padx=10, sticky='NSEW')

        self.title_size_entry = LabeledEntry(container, 'title size:')
        self.title_size_entry.grid(row=0, column=1, padx=10, sticky='NSEW')

        self.x_weight_entry = LabeledCombobox(container, 'x label weight:', values=weights)
        self.x_weight_entry.grid(row=1, column=0, padx=10, sticky='NSEW')

        self.x_size_entry = LabeledEntry(container, 'x label size:')
        self.x_size_entry.grid(row=1, column=1, padx=10, sticky='NSEW')
        
        self.y1_weight_entry = LabeledCombobox(container, 'y1 label weight:', values=weights)
        self.y1_weight_entry.grid(row=2, column=0, padx=10, sticky='NSEW')

        self.y1_size_entry = LabeledEntry(container, 'y1 label size:')
        self.y1_size_entry.grid(row=2, column=1, padx=10, sticky='NSEW')
        
        self.y2_weight_entry = LabeledCombobox(container, 'y2 label weight:', values=weights)
        self.y2_weight_entry.grid(row=3, column=0, padx=10, sticky='NSEW')

        self.y2_size_entry = LabeledEntry(container, 'y2 label size:')
        self.y2_size_entry.grid(row=3, column=1, padx=10, sticky='NSEW')

    @property
    def title_weight(self):
        return self.title_weight_entry.get()

    @title_weight.setter
    def title_weight(self, value):
        self.title_weight_entry.set(value)

    @property
    def x_weight(self):
        return self.x_weight_entry.get()

    @x_weight.setter
    def x_weight(self, value):
        self.x_weight_entry.set(value)

    @property
    def y1_weight(self):
        return self.y1_weight_entry.get()

    @y1_weight.setter
    def y1_weight(self, value):
        self.y1_weight_entry.set(value)

    @property
    def y2_weight(self):
        return self.y2_weight_entry.get()

    @y2_weight.setter
    def y2_weight(self, value):
        self.y2_weight_entry.set(value)

    @property
    def title_size(self):
        return float(self.title_size_entry.get())

    @title_size.setter
    def title_size(self, value):
        self.title_size_entry.set(value)

    @property
    def x_size(self):
        return float(self.x_size_entry.get())

    @x_size.setter
    def x_size(self, value):
        self.x_size_entry.set(value)

    @property
    def y1_size(self):
        return float(self.y1_size_entry.get())

    @y1_size.setter
    def y1_size(self, value):
        self.y1_size_entry.set(value)

    @property
    def y2_size(self):
        return float(self.y2_size_entry.get())

    @y2_size.setter
    def y2_size(self, value):
        self.y2_size_entry.set(value)


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
        color_choice.set(random.choice(list(plot_colors.keys())))
        color_combo = ttk.Combobox(container, textvariable=color_choice,
                                   width=COMBO_WIDTH, state='readonly')
        color_combo['values'] = list(plot_colors.keys())
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
            # for i, c in enumerate(y):
            for i in range(len(y)):
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
        color_choice.set(random.choice(list(plot_colors.keys())))
        color_combo = ttk.Combobox(container, textvariable=color_choice,
                                   width=COMBO_WIDTH, state='readonly')
        color_combo['values'] = list(plot_colors.keys())
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
