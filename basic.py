import math
import numpy as np
import pandas as pd
import lemons.gui as gui
import tkinter as tk
from tkinter import ttk
import re

import matplotlib.pyplot as plt

import os
from controls import LimitLines, ToleranceBands
from settings import plot_colors


class BasicFile(gui.ScrollableTab):
    """A scrollable notebook tab that supports dynamically creating and deleting basic
    rows (plots), and stores all of the user-specified information about each plot."""

    def __init__(self, notebook, filepath, app):
        """Initialize the scrollable notebook tab as well as the lists that will hold
        references to each field in each row. Creates the data start row, label row,
        and unit row entry fields for the file and adds a single row by default."""

        self.filepath = filepath
        self.filename = self.filepath.split('/')[-1]
        gui.ScrollableTab.__init__(self, notebook, self.filename, cwidth=571, cheight=252)

        # Store a reference to the root/main application
        self.app = app
        # self.app = self.nametowidget(self.winfo_toplevel())
        # print(self.nametowidget(self.app))

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

        self.app.clipboard['title'] = self._titles[ID].get()
        self.app.clipboard['x column'] = self._x_columns[ID].get()
        self.app.clipboard['y1 columns'] = self._y1_columns[ID].get()
        self.app.clipboard['y2 columns'] = self._y2_columns[ID].get()
        self.app.clipboard['x label'] = self._x_labels[ID].get()
        self.app.clipboard['y1 label'] = self._y1_labels[ID].get()
        self.app.clipboard['y2 label'] = self._y2_labels[ID].get()

    def paste(self, ID):
        """Pastes the contents of the clipboards into the selected row."""

        self.clear(ID)
        self._titles[ID].insert(0, self.app.clipboard['title'])
        self._x_columns[ID].insert(0, self.app.clipboard['x column'])
        self._y1_columns[ID].insert(0, self.app.clipboard['y1 columns'])
        self._y2_columns[ID].insert(0, self.app.clipboard['y2 columns'])
        self._x_labels[ID].insert(0, self.app.clipboard['x label'])
        self._y1_labels[ID].insert(0, self.app.clipboard['y1 label'])
        self._y2_labels[ID].insert(0, self.app.clipboard['y2 label'])

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
                y1_colors = ['k', 'b', 'r', 'g', plot_colors['purple'], plot_colors['orange'],
                            plot_colors['brown']]
                # Create a copy of the primary axis plot colors
                y1_plot_colors = y1_colors[:]
                # Choose colors for the secondary axis - will be iterated-through sequentially
                y2_colors = [plot_colors['gray'], 'c', plot_colors['pink'], plot_colors['lime'],
                            'm', plot_colors['gold'], 'y']
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

                # If the controls window has not been created yet, create it and leave it hidden
                if not flipbook.controls:
                    flipbook.controls = Controls(flipbook, flipbook.plots[flipbook.page])
                    flipbook.controls.withdraw()

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
                        flipbook.primary.plot(self.x, plus[1], plot_colors[self.color[p]],
                                        linestyle=self.linestyle[p])
                    elif plus[0] == 'secondary':
                        flipbook.secondary.plot(self.x, plus[1], plot_colors[self.color[p]],
                                        linestyle=self.linestyle[p])
                # Iterate through the minus bands of the current plot
                for m, minus in enumerate(self.minus_bands):
                    # If there are no minus bands, skip to next iteration
                    if not minus: continue
                    # Plot the minus band on the appropriate axis
                    elif minus[0] == 'primary':
                        flipbook.primary.plot(self.x, minus[1], plot_colors[self.color[m]],
                                        linestyle=self.linestyle[m])
                    elif minus[0] == 'secondary':
                        flipbook.secondary.plot(self.x, minus[1], plot_colors[self.color[m]],
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
                                    color=plot_colors[self.line_color[v]],
                                    alpha=float(self.line_alpha[v]))
                    elif self.line_orientation[v] == 'horizontal':
                        axis.axhline(y=float(self.line_value[v]),
                                    linestyle=self.line_style[v],
                                    color=plot_colors[self.line_color[v]],
                                    alpha=float(self.line_alpha[v]))

                flipbook.controls.refresh()

        # Create a new plot object and hold a reference to it
        plot = Plot()
        self.plots.append(plot)

    def _filetype(self, path):
        """Determine the filetype of the input."""

        _, extension = os.path.splitext(path)
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

