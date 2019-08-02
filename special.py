import math
import numpy as np
import pandas as pd
import lemons.gui as gui
import tkinter as tk
from tkinter import ttk
import re

import matplotlib.pyplot as plt


class PeakValleyFile(gui.ScrollableTab):

	def __init__(self, notebook, filepath):

		self.filepath = filepath
		self.filename = self.filepath.split('/')[-1]
		gui.ScrollableTab.__init__(self, notebook, self.filename, cwidth=571, cheight=252)
		self.columnconfigure(0, weight=1)

		self._count = 0
		self._rows = []
		self._sections = []
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

		# label_label = tk.Label(info, text='Label row:')
		# label_label.grid(row=0, column=0, padx=5)

		# label_entry = ttk.Entry(info, width=10)
		# label_entry.grid(row=0, column=1, sticky='EW')

		count_label = tk.Label(info, text='count:')
		count_label.grid(row=0, column=0, padx=5, sticky='E')

		self.count_combo = ttk.Combobox(info, width=7, state='readonly')
		self.count_combo['values'] = ['cycles', 'segments']
		self.count_combo.grid(row=0, column=1, sticky='EW')
		self.count_combo.set('cycles')

		delimiter_label = tk.Label(info, text='delimiter:')
		delimiter_label.grid(row=1, column=0, padx=5, sticky='E')

		self.delimiter_combo = ttk.Combobox(info, width=7, state='readonly')
		self.delimiter_combo['values'] = ['comma', 'tab']
		self.delimiter_combo.grid(row=1, column=1, sticky='EW')
		self.delimiter_combo.set('tab')

		criteria = tk.Frame(controls)
		criteria.grid(row=0, column=1, padx=20, sticky='NSEW')
		criteria.columnconfigure(1, weight=1)
		criteria.rowconfigure(0, weight=1)
		criteria.rowconfigure(1, weight=1)

		lower_label = tk.Label(criteria, text='Lower fail range:')
		lower_label.grid(row=0, column=0, sticky='E')

		self.lower_entry = ttk.Entry(criteria, width=10)
		self.lower_entry.grid(row=0, column=1, padx=5, sticky='EW')

		upper_label = tk.Label(criteria, text='Upper fail range:')
		upper_label.grid(row=1, column=0, sticky='E')

		self.upper_entry = ttk.Entry(criteria, width=10)
		self.upper_entry.grid(row=1, column=1, padx=5, sticky='EW')

		checkboxes = tk.Frame(controls)
		checkboxes.grid(row=0, column=2, padx=(0, 20), sticky='NSEW')
		checkboxes.columnconfigure(0, weight=1)

		self.convert = tk.IntVar()
		self.convert_checkbox = ttk.Checkbutton(checkboxes, text='Convert to cycles', takefocus=0, variable=self.convert)
		self.convert_checkbox.grid(row=0, column=0, sticky='EW')
		self.convert_checkbox.state(['!alternate', 'selected'])

		self.zero = tk.IntVar()
		self.zero_checkbox = ttk.Checkbutton(checkboxes, text='Zero-out counter column', takefocus=0, variable=self.zero)
		self.zero_checkbox.grid(row=1, column=0, sticky='EW')
		self.zero_checkbox.state(['!alternate', 'selected'])

		self.split = tk.IntVar()
		self.split_checkbox = ttk.Checkbutton(checkboxes, text='Split peaks and valleys', takefocus=0, variable=self.split)
		self.split_checkbox.grid(row=2, column=0, sticky='EW')
		self.split_checkbox.state(['!alternate', 'selected'])

		self.read_button = ttk.Button(controls, text='Read', width=10)
		self.read_button['command'] = self.read
		self.read_button.grid(row=1, column=0, columnspan=3, pady=(80, 0))


	def add_row(self):

		# Don't allow for rows to be added until the read has been completed
		if not self.READ_COMPLETE: return
		
		MARGIN = 8
		PADDING = 10
		WIDTH = 7

		# Destroy the read button
		if self._count == 0: self.read_button.destroy()

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

		sections_label = ttk.Label(controls, text='section:')
		sections_label.grid(row=0, column=0, padx=PADDING)
		sections_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		sections_entry.grid(row=1, column=0, padx=PADDING, sticky="EW")
		self._sections.append(sections_entry)

		x_column_label = ttk.Label(controls, text='x-column:')
		x_column_label.grid(row=0, column=1, padx=PADDING)
		x_column_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		x_column_entry.grid(row=1, column=1, padx=PADDING, sticky="EW")
		self._x_columns.append(x_column_entry)

		y_column_label = ttk.Label(controls, text='y-column:')
		y_column_label.grid(row=0, column=2, padx=PADDING)
		y_column_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		y_column_entry.grid(row=1, column=2, padx=PADDING, sticky="EW")
		self._y_columns.append(y_column_entry)

		label_label = tk.Label(controls, text='label row:')
		label_label.grid(row=0, column=3, padx=PADDING)
		label_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		label_entry.grid(row=1, column=3, padx=PADDING, sticky="EW")
		self._labels.append(label_entry)

		unit_label = tk.Label(controls, text='unit row:')
		unit_label.grid(row=0, column=4, padx=PADDING)
		unit_entry = ttk.Combobox(controls, state='readonly', width=WIDTH)
		unit_entry.grid(row=1, column=4, padx=PADDING, sticky="EW")
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


	def read(self):
		
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

			def parse_header(self, start, end):
				self.header = pd.DataFrame(self.raw_data[start:end+1])
				self.header_length = len(self.header.index)
				self.parse_datetime()

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


	# def calculate(self):
	# 	with open(self.filepath, 'rb') as file:
	# 		raw = [line.rstrip().decode('latin-1').split('\t') for line in file]
	# 		data = pd.DataFrame(raw)
	# 		print(data)
	# 		print(data.iloc[:, [0]])


	def add_plot(self):
		"""Create a new plot object and hold a reference to it."""

		class Plot:
			"""Object that holds information about a singular plot."""

			# def __init__(self):
			# 	self.FAILURES_DETERMINED = False
			# 	self.DATA_SPLIT = False

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

			def split(self):
				# average = sum(self.y1) / len(self.y1)
				# x_valleys = self.x[self.y1 < average]
				# x_peaks = self.x[self.y1 > average]
				# y_valleys = self.y1[self.y1 < average]
				# y_peaks = self.y1[self.y1 > average]
				# self.x = [x_valleys, x_peaks]
				# self.y1 = [y_valleys, y_peaks]

				if not self.FAILURES_DETERMINED:
					average = sum(self.y1) / len(self.y1)
					x_valleys = self.x[self.y1 < average]
					x_peaks = self.x[self.y1 > average]
					y_valleys = self.y1[self.y1 < average]
					y_peaks = self.y1[self.y1 > average]
					self.x = [x_valleys, x_peaks]
					self.y1 = [y_valleys, y_peaks]
				else:
					average = sum(self.y1[1]) / len(self.y1[1])
					x_valleys = self.x[1][self.y1[1] < average]
					x_peaks = self.x[1][self.y1[1] > average]
					y_valleys = self.y1[1][self.y1[1] < average]
					y_peaks = self.y1[1][self.y1[1] > average]
					self.x = [self.x[0], x_valleys, x_peaks]
					self.y1 = [self.y1[0], y_valleys, y_peaks]

				self.DATA_SPLIT = True

			def _generate(self, section, labels, x_column, y_column, units=None):
				"""The main function for the object which stores the inputs and calls
				other relevant functions."""

				# Reset certain variables each time this function runs
				# (typically when the plot button is pressed)
				self.FAILURES_DETERMINED = False
				self.DATA_SPLIT = False

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
				# self.x_original = self._x_data(x_column)
				# self.y1_original = self._y_data(y_column)
				# self.x = [self.x_original]
				# self.y1 = [self.y1_original]
				# self.x = [self._x_data(self.x_column)]
				# self.y1 = [self._y_data(self.y_column)]

				self.section.parse_labels(labels)
				self.labels = self.section.labels
				self.section.parse_units(units)
				self.units = self.section.units

			def update_plot(self, flipbook, file_number, plot_number):
				# =================
				# MAIN UPDATE LOGIC
				# =================

				# Display the filename of the current plot
				flipbook.filename.set(f'{flipbook.info[file_number].filename} - Plot {plot_number + 1}')

				# Essentially reset the secondary axis by clearing and turning it off if it exists,
				# then setting the self.secondary variable to None
				if flipbook.secondary:
				    flipbook.secondary.clear()
				    flipbook.secondary.axis('off')
				flipbook.secondary = None

				# Create a variable that keeps track of if a secondary axis is necessary
				self.secondary_axis = False

				# Clear the primary axis as well
				flipbook.primary.clear()

				# Set the appropriate coordinates format to display on the flipbook
				flipbook.primary.set_zorder(1000)
				flipbook.primary.format_coord = flipbook._coordinates(flipbook.primary, None, self.secondary_axis)

				colors = {'pass': 'g', 'fail': 'r', 'valley': 'c', 'peak': 'k'}
				if not self.FAILURES_DETERMINED and not self.DATA_SPLIT:
					flipbook.primary.scatter(self.x, self.y1, color='k')
				elif self.FAILURES_DETERMINED and self.DATA_SPLIT:
					flipbook.primary.scatter(self.x[0], self.y1[0], color=colors['fail'])
					flipbook.primary.scatter(self.x[1], self.y1[1], color=colors['valley'])
					flipbook.primary.scatter(self.x[2], self.y1[2], color=colors['peak'])
				elif self.FAILURES_DETERMINED and not self.DATA_SPLIT:
					flipbook.primary.scatter(self.x[0], self.y1[0], color=colors['fail'])
					flipbook.primary.scatter(self.x[1], self.y1[1], color=colors['pass'])
				elif not self.FAILURES_DETERMINED and self.DATA_SPLIT:
					flipbook.primary.scatter(self.x[0], self.y1[0], color=colors['valley'])
					flipbook.primary.scatter(self.x[1], self.y1[1], color=colors['peak'])

				# Determine adequate padding for the x-axis and set the x-axis limits accordingly.
				# Store the original x-axis limits to allow the user to revert to them if desired.
				min_x = min(self.x_original.dropna())
				max_x = max(self.x_original.dropna())
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


if __name__ == '__main__':

	def plot():
		tab.lower_entry.insert(0, '0.115')
		tab.upper_entry.insert(0, '0.295')
		tab.generate()
		for p, plot in enumerate(tab.plots):
			plt.plot(plot.x, plot.y1)
			plt.show()

	filepath = 'testdata.dat'
	app = gui.Application(padding=20)
	notebook = ttk.Notebook(app)
	notebook.grid(row=0, column=0, sticky='NSEW')
	tab = PeakValleyFile(notebook, filepath)
	buttons = tk.Frame(app)
	buttons.grid(row=1, column=0, sticky='NSEW')
	add_button = ttk.Button(buttons, text='+')
	add_button['command'] = tab.add_row
	add_button.grid(row=0, column=0, sticky='W')
	delete_button = ttk.Button(buttons, text='-')
	delete_button['command'] = tab.delete_row
	delete_button.grid(row=0, column=1, sticky='W')
	plot_button = ttk.Button(buttons, text='Plot')
	plot_button['command'] = plot
	plot_button.grid(row=0, column=2, sticky='W')
	app.mainloop()