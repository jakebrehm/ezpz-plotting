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

                # flipbook.controls.refresh()

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


class BasicControls(ttk.Notebook):

    def __init__(self, *args, **kwargs):

        ttk.Notebook.__init__(self, *args, **kwargs)
        
        # Add scrollable tabs to the notebook
        figure = gui.ScrollableTab(self, 'Figure', cheight=400, cwidth=400)
        appearance = gui.ScrollableTab(self, 'Appearance', cheight=400, cwidth=400)
        analysis = gui.ScrollableTab(self, 'Analysis', cheight=400, cwidth=400)
        annotations = gui.ScrollableTab(self, 'Annotations', cheight=400, cwidth=400)

        self.current = None
        self.flipbook = None

        self.band_controls = None # Tolerance band controls object
        self.line_controls = None # Limit lines controls object

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
        # background_combo.bind('<<ComboboxSelected>>', self._custom_background)

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

        # # Refresh the controls with values for the current plot
        # self.refresh()

        # # Bind the enter key to the same function the update button calls
        # self.bind('<Return>', self.update)















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


    def update(self):
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
















        
    def _custom_background(self, event=None):
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

