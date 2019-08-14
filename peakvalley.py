import math
import numpy as np
import pandas as pd
import lemons.gui as gui
import tkinter as tk
from tkinter import ttk
import re

import matplotlib as mpl
import matplotlib.pyplot as plt


class PeakValleyFile(gui.ScrollableTab):

	def __init__(self, notebook, filepath, app):

		self.filepath = filepath
		self.filename = self.filepath.split('/')[-1]
		gui.ScrollableTab.__init__(self, notebook, self.filename, cwidth=571, cheight=252)
		self.columnconfigure(0, weight=1)

		self.app = app

		self._count = 0
		self._rows = []
		self._sections = []
		self._counters = []
		self._x_columns = []
		self._y_columns = []
		self._labels = []
		self._units = []

		self.plots = []

		self.READ_COMPLETE = False

		controls = tk.Frame(self)
		controls.grid(row=0, column=0, pady=20, sticky='NSEW')
		controls.columnconfigure(0, weight=1)
		controls.columnconfigure(1, weight=1)

		info = tk.Frame(controls)
		info.grid(row=0, column=0, padx=(20, 0), sticky='NSEW')
		info.columnconfigure(1, weight=1)
		info.rowconfigure(0, weight=1)
		info.rowconfigure(1, weight=1)

		delimiter_label = tk.Label(info, text='delimiter:')
		delimiter_label.grid(row=0, column=0, padx=5, sticky='E')

		self.delimiter_combo = ttk.Combobox(info, width=7, state='readonly')
		self.delimiter_combo['values'] = ['comma', 'tab']
		self.delimiter_combo.grid(row=0, column=1, sticky='EW')
		self.delimiter_combo.set('tab')

		self.read_button = ttk.Button(info, text='Read File', width=15)
		self.read_button['command'] = self.read
		self.read_button.grid(row=1, column=0, columnspan=2)

		criteria = tk.Frame(controls)
		criteria.grid(row=0, column=1, padx=20, sticky='NSEW')
		criteria.columnconfigure(1, weight=1)
		criteria.rowconfigure(0, weight=1)
		criteria.rowconfigure(1, weight=1)

		lower_label = tk.Label(criteria, text='Valley Maximum:')
		lower_label.grid(row=0, column=0, sticky='E')

		self.lower_entry = ttk.Entry(criteria, width=10)
		self.lower_entry.grid(row=0, column=1, padx=5, sticky='EW')

		upper_label = tk.Label(criteria, text='Peak Minimum:')
		upper_label.grid(row=1, column=0, sticky='E')

		self.upper_entry = ttk.Entry(criteria, width=10)
		self.upper_entry.grid(row=1, column=1, padx=5, sticky='EW')

		checkboxes = tk.Frame(controls)
		checkboxes.grid(row=0, column=2, padx=(0, 20), sticky='NSEW')
		checkboxes.columnconfigure(0, weight=1)

		self.convert = tk.IntVar()
		self.convert_checkbox = ttk.Checkbutton(checkboxes, takefocus=0,
												variable=self.convert)
		self.convert_checkbox['text'] = 'Convert to cycles'
		self.convert_checkbox.grid(row=0, column=0, sticky='EW')
		self.convert_checkbox.state(['!alternate', 'selected'])

		self.zero = tk.IntVar()
		self.zero_checkbox = ttk.Checkbutton(checkboxes, takefocus=0,
											 variable=self.zero)
		self.zero_checkbox['text'] = 'Zero-out counter column'
		self.zero_checkbox.grid(row=1, column=0, sticky='EW')
		self.zero_checkbox.state(['!alternate', 'selected'])

		self.split = tk.IntVar()
		self.split_checkbox = ttk.Checkbutton(checkboxes, takefocus=0,
											  variable=self.split)
		self.split_checkbox['text'] = 'Split peaks and valleys'
		self.split_checkbox.grid(row=2, column=0, sticky='EW')
		self.split_checkbox.state(['!alternate', 'selected'])

		self._disable_header()


	def _update_combobox(self, plot, sections):

		p = plot - 1

		self._sections[p]['values'] = list(range(1, sections + 1))
		self._sections[p].set(1)

		columns = self.sections[p].columns
		self._x_columns[p]['values'] = list(range(1, columns + 1))
		self._x_columns[p].set(1)

		columns = self.sections[p].columns
		self._y_columns[p]['values'] = list(range(1, columns + 1))
		self._y_columns[p].set(2)

		rows = self.sections[p].header_length
		self._units[p]['values'] = list(range(1, rows + 1))
		self._units[p].set(rows)
		self._labels[p]['values'] = list(range(1, rows + 1))
		self._labels[p].set(1)


	def _disable_header(self):
		self.lower_entry['state'] = 'disabled'
		self.upper_entry['state'] = 'disabled'
		self.convert_checkbox.state(['disabled'])
		self.zero_checkbox.state(['disabled'])
		self.split_checkbox.state(['disabled'])


	def _enable_header(self):
		self.lower_entry['state'] = 'normal'
		self.upper_entry['state'] = 'normal'
		self.convert_checkbox.state(['!disabled', 'selected'])
		self.zero_checkbox.state(['!disabled', 'selected'])
		self.split_checkbox.state(['!disabled', 'selected'])
		self.set_default_focus()


	def _section_changed(self, event):
		if event.widget in self._sections:
			index = self._sections.index(event.widget)
			counter_combo = self._counters[index]
			section = int(event.widget.get())
			counter_type = self.sections[section - 1].counter
			counter_combo.set(counter_type)


	def add_row(self):

		# Don't allow for rows to be added until the read has been completed
		if not self.READ_COMPLETE: return
		
		MARGIN = 8
		PADDING = 6
		WIDTH = 6

		# Destroy the read button
		# if self._count == 0: self.read_button.destroy()
		if self._count == 0:
			self.read_button['text'] = 'Read Successful'
			self.read_button['state'] = 'disabled'

		frame = tk.LabelFrame(self, text=f'Plot {self._count + 1}')
		frame.grid(row=self._count + 1, column=0,
				   padx=MARGIN, pady=(0, MARGIN*2), sticky='NSEW')
		frame.columnconfigure(0, weight=1)

		# Create a frame that everything else will be placed inside of
		inner = tk.Frame(frame)
		inner.grid(row=0, column=0, padx=MARGIN*2, pady=MARGIN*2, sticky='NSEW')
		inner.columnconfigure(0, weight=1)
		inner.columnconfigure(1, weight=1)
		inner.columnconfigure(2, weight=1)
		inner.columnconfigure(3, weight=1)

		controls = tk.Frame(inner)
		controls.columnconfigure(0, weight=1)
		controls.columnconfigure(1, weight=1)
		controls.columnconfigure(2, weight=1)
		controls.columnconfigure(3, weight=1)
		controls.grid(row=0, column=1, sticky="EW")

		section_label = ttk.Label(controls, text='section:')
		section_label.grid(row=0, column=0, padx=PADDING)
		section_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		section_entry.grid(row=1, column=0, padx=PADDING, sticky="EW")
		section_entry.bind('<<ComboboxSelected>>', self._section_changed)
		self._sections.append(section_entry)

		counter_label = ttk.Label(controls, text='counter:')
		counter_label.grid(row=0, column=1, padx=PADDING)
		counter_entry = ttk.Combobox(controls, state='readonly', width=WIDTH+3)
		counter_entry['values'] = ['segments', 'cycles', 'other']
		counter_entry.grid(row=1, column=1, padx=PADDING, sticky="EW")
		counter_entry.set(self.sections[0].counter)
		self._counters.append(counter_entry)

		x_column_label = ttk.Label(controls, text='x-column:')
		x_column_label.grid(row=0, column=2, padx=PADDING)
		x_column_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		x_column_entry.grid(row=1, column=2, padx=PADDING, sticky="EW")
		self._x_columns.append(x_column_entry)

		y_column_label = ttk.Label(controls, text='y-column:')
		y_column_label.grid(row=0, column=3, padx=PADDING)
		y_column_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		y_column_entry.grid(row=1, column=3, padx=PADDING, sticky="EW")
		self._y_columns.append(y_column_entry)

		label_label = tk.Label(controls, text='label row:')
		label_label.grid(row=0, column=4, padx=PADDING)
		label_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		label_entry.grid(row=1, column=4, padx=PADDING, sticky="EW")
		self._labels.append(label_entry)

		unit_label = tk.Label(controls, text='unit row:')
		unit_label.grid(row=0, column=5, padx=PADDING)
		unit_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		unit_entry.grid(row=1, column=5, padx=PADDING, sticky="EW")
		self._units.append(unit_entry)

		edit_controls = tk.Frame(inner)
		edit_controls.grid(row=0, column=2, padx=(10, 0), sticky="EW")
		edit_controls.columnconfigure(0, weight=1)
		edit_controls.columnconfigure(1, weight=1)

        # Create a copy button
		copy_image = gui.RenderImage('Assets\\copy.png', downscale=12)
		copy_button = ttk.Button(edit_controls, takefocus=0, width=3, image=copy_image, text='C')
		# copy_button['command'] = lambda ID=self._count: self.copy(ID)
		copy_button.image = copy_image
		copy_button.grid(row=0, column=0, padx=PADDING/5, sticky='EW')

		# Create a paste button
		paste_image = gui.RenderImage('Assets\\paste.png', downscale=12)
		paste_button = ttk.Button(edit_controls, takefocus=0, width=3, image=paste_image, text='C')
		# paste_button['command'] = lambda ID=self._count: self.paste(ID)
		paste_button.image = paste_image
		paste_button.grid(row=0, column=1, padx=PADDING/5, sticky='EW')

		# Update the comboboxes of the GUI to display the appropriate choices
		self._update_combobox(plot=self._count+1, sections=self.section_total)

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


	def set_default_focus(self):
		self.lower_entry.focus_set()


	def read(self, event=None):
		
		class Section:

			def __init__(self, section, raw_data):

				self.raw_data = raw_data

				self.section = section

				self.header = None
				self.data = None

				self.date = None
				self.time = None

				self.labels = None
				self.units = None
				self.header_length = None
				self.columns = None

				self.counter = None

			def parse_header(self, start, end):
				self.header = pd.DataFrame(self.raw_data[start:end+1])
				self.header_length = len(self.header.index)
				self.parse_datetime()
				self.parse_counter()

			def parse_data(self, start, end):
				self.data = pd.DataFrame(self.raw_data[start:end+1])
				self.columns = len(self.data.columns)

			def parse_labels(self, row):
				self.labels = self.header.iloc[row-1, :]

			def parse_units(self, row):
				if row is not None:
					self.units = self.header.iloc[row-1, :]

			def parse_datetime(self):
				datetime = r'(\d{1,2}:\d{1,2}(:\d{1,2}\s+((AM)|(PM)))?)'
				date = r'(\d{1,2}/\d{1,2}/\d{4})'
				time = r'(\d{1,2}:\d{1,2}(:\d{1,2}\s+((AM)|(PM)))?)'
				
				header = list(self.header.values.tolist())
				for row in header:
					for item in row:
						if re.search(datetime, str(item)):
							self.date = re.findall(date, item)[0]
							self.time = re.findall(time, item)[0][0]
							return
							
			def parse_counter(self):
				header = list(self.header.values.tolist())
				for row in header:
					if 'segments' in row:
						self.counter = 'segments'
					elif 'cycles' in row:
						self.counter = 'cycles'
					else:
						self.counter = 'other'

		# Pull the delimiter from the appropriate combobox
		delimiter = self.delimiter_combo.get()
		if delimiter == 'comma': delimiter = ','
		elif delimiter == 'tab': delimiter = '\t'

		with open(self.filepath, 'rb') as file:
			raw = [line.rstrip().decode('latin-1').split(delimiter) for line in file]
		
		# Remove empty rows to avoid errors during parsing
		to_remove = []
		for r, row in enumerate(raw):
			if  len(row) == 1 and row[0] == '':
				to_remove.append(r)
		for row in sorted(to_remove, reverse=True):
			del(raw[row])

		# Determine the number of sections and where each section starts
		self.section_total = 0
		header_starts = []
		for r, row in enumerate(raw):
			# Use the 'Data Acquisition' label to find headers/separate sections
			if 'Data Acquisition' in row:
				self.section_total += 1
				header_starts.append(r)
			# Convert everything to a float to differentiate data from header
			for i, item in enumerate(row):
				try:
					raw[r][i] = float(item)
				except ValueError:
					pass

		data_starts = []
		data_ends = []
		header_ends = []
		for i, index in enumerate(header_starts):
			last_section = True if index == header_starts[-1] else False
			last_index = header_starts[i+1] if not last_section else len(raw)
			data_ends.append(last_index - 1)
			for r, row in enumerate(raw[header_starts[i]:last_index]):
				if all(isinstance(item, (int, float)) for item in row):
					data_starts.append(index + r)
					header_ends.append(index + r - 1)
					break

		self.sections = []
		for s in range(len(header_starts)):
			section = Section(section=s+1, raw_data=raw)
			section.parse_header(header_starts[s], header_ends[s])
			section.parse_data(data_starts[s], data_ends[s])
			self.sections.append(section)

		self.READ_COMPLETE = True
		self.add_row()


	def add_plot(self):
		"""Create a new plot object and hold a reference to it."""

		class Plot:
			"""Object that holds information about a singular plot."""

			def __init__(self):
				# self.FAILURES_DETERMINED = False
				# self.DATA_SPLIT = False
				self.lower = None
				self.upper = None

			def _x_data(self, x_column):
				"""Pull the appropriate x-information from the data."""

				# return self.data[self.labels[x_column-1]]
				return self.section.data.iloc[:, x_column-1]
				
			def _y_data(self, y_column):
				"""Pull the appropriate y-information from the data."""

				# return [self.data[self.labels[column-1]] for column in y_column]
				return self.section.data.iloc[:, y_column-1]

			def determine_failures(self, lower, upper):



				# self.total = len(self.y1)
				# self.failed = self.y1[(lower < self.y1) & (self.y1 < upper)]
				# self.fail_index = self.failed.index.values
				# self.fail_count = len(self.failed)
				# self.passed = self.y1[~self.y1.isin(self.failed)]
				# self.pass_index = self.passed.index.values
				# self.pass_count = len(self.passed)

				self.x_failed = self.x[(lower < self.y1) & (self.y1 < upper)]
				self.y_failed = self.y1[(lower < self.y1) & (self.y1 < upper)]
				# self.fail_index = self.y_failed.index.values

				self.x_passed = self.x[~self.y1.isin(self.y_failed)]
				self.y_passed = self.y1[~self.y1.isin(self.y_failed)]
				# self.pass_index = self.y_passed.index.values

				self.total = len(self.y1)
				self.fail_count = len(self.y_failed)
				self.pass_count = len(self.y_passed)

				self.x = [self.x_failed, self.x_passed]
				self.y1 = [self.y_failed, self.y_passed]

				self.FAILURES_DETERMINED = True
				self.lower = lower
				self.upper = upper

			def count_failures(self):
				pass

			def split(self):
				# average = sum(self.y1) / len(self.y1)
				# x_valleys = self.x[self.y1 < average]
				# x_peaks = self.x[self.y1 > average]
				# y_valleys = self.y1[self.y1 < average]
				# y_peaks = self.y1[self.y1 > average]
				# self.x = [x_valleys, x_peaks]
				# self.y1 = [y_valleys, y_peaks]

				average = sum(self.y1_original) / len(self.y1_original)
				if not self.FAILURES_DETERMINED:
					x_valleys = self.x[self.y1 < average]
					x_peaks = self.x[self.y1 > average]
					y_valleys = self.y1[self.y1 < average]
					y_peaks = self.y1[self.y1 > average]
					self.x = [x_valleys, x_peaks]
					self.y1 = [y_valleys, y_peaks]
				else:
					x_valleys = self.x[1][self.y1[1] < average]
					x_peaks = self.x[1][self.y1[1] > average]
					y_valleys = self.y1[1][self.y1[1] < average]
					y_peaks = self.y1[1][self.y1[1] > average]
					self.x = [self.x[0], x_valleys, x_peaks]
					self.y1 = [self.y1[0], y_valleys, y_peaks]

				self.DATA_SPLIT = True

			def zero(self):

				first = self.x_original.iloc[0]
				for i in range(len(self.x)):
					self.x[i] = self.x[i] - first

			def _generate(self, section, labels, x_column, y_column, units=None):
				"""The main function for the object which stores the inputs and calls
				other relevant functions."""

				# Reset certain variables each time this function runs
				# (typically when the plot button is pressed)
				self.FAILURES_DETERMINED = False
				self.DATA_SPLIT = False
				self.DATA_ZEROED = False

				# Store the inputs as instance variables
				self.section = section
				self.labels = labels
				self.units = units
				self.x_column = x_column
				self.y_column = y_column

				# Grab the relevant data and store as instance variables
				self.x = self._x_data(self.x_column)
				self.y1 = self._y_data(self.y_column)
				self.x_original = self.x.copy()
				self.y1_original = self.y1.copy()

				self.section.parse_labels(labels)
				self.labels = self.section.labels
				self.section.parse_units(units)
				self.units = self.section.units

			def update_plot(self, flipbook, file_number, plot_number):

				# Create a reference to the flipbook's primary axis for shorthand
				primary = flipbook.primary

				# Display the filename of the current plot
				filename = flipbook.info[file_number].filename
				flipbook.filename.set(f'{filename} - Plot {plot_number + 1}')

				# Essentially reset the secondary axis by clearing and turning it off if it exists,
				# then setting the self.secondary variable to None
				if flipbook.secondary:
				    flipbook.secondary.clear()
				    flipbook.secondary.axis('off')
				flipbook.secondary = None

				# Create a variable that keeps track of if a secondary axis is necessary
				self.secondary_axis = False

				# Clear the primary axis as well
				primary.clear()

				# Set the appropriate coordinates format to display on the flipbook
				primary.set_zorder(1000)
				primary.format_coord = flipbook._coordinates(flipbook.primary, None, self.secondary_axis)

				# Plot the data as a scatterplot
				colors = {'general': 'k', 'pass': 'g', 'fail': 'r', 'valley': 'c', 'peak': 'b'}
				if not self.FAILURES_DETERMINED and not self.DATA_SPLIT:
					primary.scatter(self.x, self.y1, color=colors['general'])
				elif self.FAILURES_DETERMINED and self.DATA_SPLIT:
					primary.scatter(self.x[0], self.y1[0], color=colors['fail'])
					primary.scatter(self.x[1], self.y1[1], color=colors['valley'])
					primary.scatter(self.x[2], self.y1[2], color=colors['peak'])
				elif self.FAILURES_DETERMINED and not self.DATA_SPLIT:
					primary.scatter(self.x[0], self.y1[0], color=colors['fail'])
					primary.scatter(self.x[1], self.y1[1], color=colors['pass'])
				elif not self.FAILURES_DETERMINED and self.DATA_SPLIT:
					primary.scatter(self.x[0], self.y1[0], color=colors['valley'])
					primary.scatter(self.x[1], self.y1[1], color=colors['peak'])

				# Plot horizontal lines showing pass/fail criteria
				if self.FAILURES_DETERMINED:
					primary.axhline(y=self.lower, color='r', linestyle='--', alpha=0.5)
					primary.axhline(y=self.upper, color='r', linestyle='--', alpha=0.5)

				# Determine adequate padding for the x-axis and set the x-axis limits accordingly.
				# Store the original x-axis limits to allow the user to revert to them if desired.
				min_x = min(self.x_original.dropna())
				max_x = max(self.x_original.dropna())
				padding = (max_x - min_x) * (100/90) * (0.05)
				self.x_lower_original = min_x - padding
				self.x_upper_original = max_x + padding
				primary.set_xlim(self.x_lower_original, self.x_upper_original)
				# Store the original y-axis limits to allow the user to revert to them if desired.
				self.y1_lower_original = primary.get_ylim()[0]
				self.y1_upper_original = primary.get_ylim()[1]
				if self.secondary_axis:
				    self.y2_lower_original = flipbook.secondary.get_ylim()[0]
				    self.y2_upper_original = flipbook.secondary.get_ylim()[1]

				# Turn the grid on, with both major and minor gridlines
				primary.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)
				primary.minorticks_on()
				primary.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

				# Add text boxes describing the limit lines
				props = dict(boxstyle='round', facecolor='white', alpha=0.5)
				# text = 
				# primary.text(0.80, 1.05, text, transform=primary.transAxes, fontsize=12, bbox=props)
				upper_y = float(self.upper) - 0.05*(primary.get_ylim()[1]-primary.get_ylim()[0])
				x_position = primary.get_xlim()[0] + (primary.get_xlim()[1]-primary.get_xlim()[0])/2
				primary.text(x_position, upper_y,
							 f'Minimum Peak: ({self.upper})',
							 fontsize=8, bbox=props, ha='center', va='top')
				lower_y = float(self.lower) + 0.05*(primary.get_ylim()[1]-primary.get_ylim()[0])
				primary.text(x_position, lower_y,
							 f'Maximum Valley: ({self.lower})',
							 fontsize=8, bbox=props, ha='center', va='bottom')

				# Use the seaborn plot style
				plt.style.use('seaborn')

				# Load the Tactair image and display it on the plot
				image = plt.imread(gui.ResourcePath('Assets\\tactair.bmp'))
				x_low, x_high = primary.get_xlim()
				y_low, y_high = primary.get_ylim()
				primary.imshow(image, extent=[x_low, x_high, y_low, y_high], aspect='auto')

		# Enable the header
		self._enable_header()

		# Create a new plot object and hold a reference to it
		plot = Plot()
		self.plots.append(plot)


	def generate(self):
		"""The main function for the object which pulls all of the relevant data
		from the file and adds the appropriate information to the plot objects."""

		# Store the current checkbox values
		convert = self.convert_checkbox.instate(['selected'])
		zero = self.zero_checkbox.instate(['selected'])
		split = self.split_checkbox.instate(['selected'])

		# Store the label row and corresponding labels as instance variables
		lower = float(self.lower_entry.get()) if self.lower_entry.get() else None
		upper = float(self.upper_entry.get()) if self.upper_entry.get() else None

		for p, plot in enumerate(self.plots):
			section_number = int(self._sections[p].get())
			section = self.sections[section_number-1]

			label_row = int(self._labels[p].get())
			unit_row = int(self._units[p].get()) if self._units[p].get() else None
			x_column = int(self._x_columns[p].get())
			y_column = int(self._y_columns[p].get())

			plot._generate(section, label_row, x_column, y_column, unit_row)

			# Determine how many failures there are before modifying plot.x
			# and plot.y any further
			if lower is not None and upper is not None:
				plot.determine_failures(lower, upper)

			if split: plot.split()
			if zero: plot.zero()


class PeakValleyControls(ttk.Notebook):

	def __init__(self, *args, **kwargs):

		ttk.Notebook.__init__(self, *args, **kwargs)
		
		# Add scrollable tabs to the notebook
		figure = gui.ScrollableTab(self, 'Figure', cheight=400, cwidth=400)
		appearance = gui.ScrollableTab(self, 'Appearance', cheight=400, cwidth=400)
		analysis = gui.ScrollableTab(self, 'Analysis', cheight=400, cwidth=400)
		annotations = gui.ScrollableTab(self, 'Annotations', cheight=400, cwidth=400)

		self.current = None
		self.flipbook = None


	def refresh(self):
		"""Refresh the controls window fields with the currently stored values."""

		# # Get a reference to the current plot object
		# current = self.current

		pass

	def update(self):
		"""Update the current plot object with the user-entered values and refresh
		both the plot and the controls window."""

		# # Get a reference to the current plot object
		# current = self.current

		pass

		# # Update the plot and refresh the controls window
		# self.flipbook.update_plot()
		# self.refresh()


if __name__ == '__main__':

	def read():
		tab.read()
		tab.lower_entry.insert(0, '0.115')
		tab.upper_entry.insert(0, '0.295')

	def plot():
		tab._sections[0].set('4')
		tab._y_columns[0].set('3')
		tab._labels[0].set('2')
		tab.generate()
		# for p, plot in enumerate(tab.plots):
		# 	plt.plot(plot.x, plot.y1)
		# 	plt.show()
		print(tab.plots[0].x, end='\n\n')
		# print(tab.plots[0].x_original, end='\n\n')
		# print(tab.plots[0].y1_original, end='\n\n')

	def both():
		read()
		plot()

	filepath = 'Data\\peakvalley.dat'
	app = gui.Application(padding=20)
	notebook = ttk.Notebook(app)
	notebook.grid(row=0, column=0, sticky='NSEW')
	tab = PeakValleyFile(notebook, filepath, app)
	buttons = tk.Frame(app)
	buttons.grid(row=1, column=0, sticky='NSEW')
	add_button = ttk.Button(buttons, text='+')
	add_button['command'] = tab.add_row
	add_button.grid(row=0, column=0, sticky='W')
	delete_button = ttk.Button(buttons, text='-')
	delete_button['command'] = tab.delete_row
	delete_button.grid(row=0, column=1, sticky='W')
	read_button = ttk.Button(buttons, text='Read')
	read_button['command'] = read
	read_button.grid(row=0, column=2, sticky='W')
	plot_button = ttk.Button(buttons, text='Plot')
	plot_button['command'] = plot
	plot_button.grid(row=0, column=3, sticky='W')
	both_button = ttk.Button(buttons, text='Both')
	both_button['command'] = both
	both_button.grid(row=0, column=4, sticky='W')
	app.bind('<Return>', both)
	app.mainloop()