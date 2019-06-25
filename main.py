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
    matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
if platform.system() == 'Windows':
    matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Data science packages
import pandas as pd
import math

# Miscellaneous packages
import re
import configobj
import random

def save_preset():
    valid = (('Configuration Files (*.ini)', '*.ini'),('All Files',"*.*"))
    location = fd.asksaveasfilename(title='Choose where to save the preset file',
                                    defaultextension='.ini',
                                    filetypes=valid)
    preset = configobj.ConfigObj(location)

    for f, file in enumerate(files):
        preset[f'File {f+1}'] = {
            'filepath': inputs[f],
            'data start': file.data_row_entry.get(),
            'label row': file.label_row_entry.get(),
            'unit row': file.unit_row_entry.get() if file.unit_row_entry.get() else '',
        }

        for n, section in enumerate(file.plots):
            preset[f'File {f+1}'][f'Plot {n+1}'] = {
                'title': files[f]._titles[n].get(),
                'x column': files[f]._x_columns[n].get(),
                'y1 columns': files[f]._y1_columns[n].get(),
                'y2 columns': files[f]._y2_columns[n].get(),
                'x label': files[f]._x_labels[n].get(),
                'y1 label': files[f]._y1_labels[n].get(),
                'y2 label': files[f]._y2_labels[n].get(),
            }

    preset.write()


def load_preset():
    global inputs, files

    location = fd.askopenfilename(title='Choose the preset file')
    preset = configobj.ConfigObj(location)

    if len(preset) == 0:
        message = 'It looks like the preset file you chose is either empty or not ' \
                  'formatted correctly. Please double check the file and try again.'
        mb.showinfo('Oops!', message)
        return

    inputs = [info['filepath'] for file, info in preset.items()]

    listbox.clear()
    listbox.field['state'] = 'normal'
    for filepath in inputs: listbox.field.insert('end', ' ' + filepath)
    listbox.field['state'] = 'disable'
    listbox.field['justify'] = 'left'

    enable()
    input_controls()

    for f, (file, info) in enumerate(preset.items()):
        if len(info) > 5:
            rows_needed = len(info) - 5
            for _ in range(rows_needed): plus_row(tab=f)

    for f, (file, info) in enumerate(preset.items()):
        files[f].data_row_entry.insert(0, info['data start'])
        files[f].label_row_entry.insert(0, info['label row'])
        files[f].unit_row_entry.insert(0, info['unit row'])
        plots = [key for key in info.keys()
                 if key not in ['filepath', 'data start', 'label row', 'unit row']]

        for p, plot in enumerate(plots):
            files[f]._titles[p].insert(0, info[plot]['title'])
            files[f]._x_columns[p].insert(0, info[plot]['x column'])
            files[f]._y1_columns[p].insert(0, info[plot]['y1 columns'])
            files[f]._y2_columns[p].insert(0, info[plot]['y2 columns'])
            files[f]._x_labels[p].insert(0, info[plot]['x label'])
            files[f]._y1_labels[p].insert(0, info[plot]['y1 label'])
            files[f]._y2_labels[p].insert(0, info[plot]['y2 label'])


def browse():
    global inputs
    if listbox.get():
        inputs = listbox.get()
        enable()
        input_controls()


def enable():
    plot_button['state'] = 'normal'
    plus_button['state'] = 'normal'
    minus_button['state'] = 'normal'

    file_menu.entryconfig(1, state='normal')
    file_menu.entryconfig(2, state='normal')
    file_menu.entryconfig(4, state='normal')
    edit_menu.entryconfig(0, state='normal')
    edit_menu.entryconfig(1, state='normal')

    edit_menu.entryconfig(3, state='normal')
    edit_menu.entryconfig(4, state='normal')


def reset():
    listbox.clear()

    plot_button['state'] = 'disabled'
    plus_button['state'] = 'disabled'
    minus_button['state'] = 'disabled'

    file_menu.entryconfig(1, state='disabled')
    file_menu.entryconfig(2, state='disabled')
    file_menu.entryconfig(4, state='disabled')
    edit_menu.entryconfig(0, state='disabled')
    edit_menu.entryconfig(1, state='disabled')

    edit_menu.entryconfig(3, state='disabled')
    edit_menu.entryconfig(4, state='disabled')

    for child in primary.winfo_children(): child.destroy()

    message = 'Please provide at least one input file.\n\nControls will appear here.'
    no_input_label = tk.Label(primary, text=message)
    no_input_label.grid(row=0, column=0, sticky='NSEW')


def input_controls():
    global primary, notebook, files

    for child in primary.winfo_children(): child.destroy()

    notebook = ttk.Notebook(primary, takefocus=0)
    notebook.grid(row=0, column=0, sticky='NSEW')

    files = []
    for filepath in inputs:
        file = File(notebook, filepath)
        files.append(file)
    files[0].data_row_entry.focus_set()


def plus_row(event=None, tab=None):
    try:
        if not tab: tab = notebook.index(notebook.select())
        files[tab].add_row()
    except NameError: pass


def minus_row(event=None, tab=None):
    try:
        if not tab: tab = notebook.index(notebook.select())
        files[tab].delete_row()
    except NameError: pass


def add_file():
    global inputs
    filepath = fd.askopenfilename(title='Choose the preset file')
    if len(filepath) == 0: return
    inputs.append(filepath)
    file = File(notebook, filepath)
    files.append(file)
    listbox.field['state'] = 'normal'
    listbox.field.insert('end', filepath)
    listbox.field['state'] = 'disable'
    listbox.field['justify'] = 'left'


def remove_file():
    global files
    if not len(files) > 1: return
    current = notebook.index(notebook.select())
    del(inputs[current])
    del(files[current])
    app.root.nametowidget(notebook.select()).destroy()
    listbox.field['state'] = 'normal'
    listbox.field.delete(current)
    listbox.field['state'] = 'disable'
    listbox.field['justify'] = 'left'


def switch_tab(event, direction):
    try:
        current = notebook.index(notebook.select())
        destination = (current + 1) if direction == 'next' else (current - 1)
        notebook.select(destination)
    except (NameError, tk.TclError):
        pass
    else:
        files[destination].data_row_entry.focus_set()


def plot_function(event=None):
    for file in files: file.generate()
    flipbook = Flipbook(app.root, info=files)


def paste_file():
    current = notebook.index(notebook.select())
    for row in range(len(files[current]._rows)):
        if clipboard['title']:
            files[current]._titles[row].delete(0, 'end')
            files[current]._titles[row].insert(0, clipboard['title'])
        if clipboard['x column']:
            files[current]._x_columns[row].delete(0, 'end')
            files[current]._x_columns[row].insert(0, clipboard['x column'])
        if clipboard['y1 columns']:
            files[current]._y1_columns[row].delete(0, 'end')
            files[current]._y1_columns[row].insert(0, clipboard['y1 columns'])
        if clipboard['y2 columns']:
            files[current]._y2_columns[row].delete(0, 'end')
            files[current]._y2_columns[row].insert(0, clipboard['y2 columns'])
        if clipboard['x label']:
            files[current]._x_labels[row].delete(0, 'end')
            files[current]._x_labels[row].insert(0, clipboard['x label'])
        if clipboard['y1 label']:
            files[current]._y1_labels[row].delete(0, 'end')
            files[current]._y1_labels[row].insert(0, clipboard['y1 label'])
        if clipboard['y2 label']:
            files[current]._y2_labels[row].delete(0, 'end')
            files[current]._y2_labels[row].insert(0, clipboard['y2 label'])


def paste_all():
    for file in files:
        for row in range(len(file._rows)):
            if clipboard['title']:
                file._titles[row].delete(0, 'end')
                file._titles[row].insert(0, clipboard['title'])
            if clipboard['x column']:
                file._x_columns[row].delete(0, 'end')
                file._x_columns[row].insert(0, clipboard['x column'])
            if clipboard['y1 columns']:
                file._y1_columns[row].delete(0, 'end')
                file._y1_columns[row].insert(0, clipboard['y1 columns'])
            if clipboard['y2 columns']:
                file._y2_columns[row].delete(0, 'end')
                file._y2_columns[row].insert(0, clipboard['y2 columns'])
            if clipboard['x label']:
                file._x_labels[row].delete(0, 'end')
                file._x_labels[row].insert(0, clipboard['x label'])
            if clipboard['y1 label']:
                file._y1_labels[row].delete(0, 'end')
                file._y1_labels[row].insert(0, clipboard['y1 label'])
            if clipboard['y2 label']:
                file._y2_labels[row].delete(0, 'end')
                file._y2_labels[row].insert(0, clipboard['y2 label'])


def clear_all():
    for file in files:
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


clipboard = {
        'title': None,
        'x column': None,
        'y1 columns': None,
        'y2 columns': None,
        'x label': None,
        'y1 label': None,
        'y2 label': None,
    }


# colors = {
#         'blue': 'b',
#         'green': 'g',
#         'red':  'r',
#         'cyan': 'c',
#         'magenta': 'm',
#         'yellow': 'y',
#         'white': 'w',
#         'black': 'k',
# }


plot_colors = {
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
}

class Flipbook(tk.Toplevel):

    def __init__(self, *args, info, **kwargs):

        self.info = info
        self.page = 0
        self.pages = sum(file._count for file in info) - 1
        self.plots = [plot for file in self.info for plot in file.plots]
        self.files = [f for f, file in enumerate(self.info) for _ in range(len(file.plots))]
        self.numbers = [p for f, file in enumerate(self.info) for p in range(len(file.plots))]
        self.secondary = None
        self.controls = None
        self.band_controls = None

        tk.Toplevel.__init__(self, *args, **kwargs)

        self.title('Flipbook')
        self.resizable(width=False, height=False)
        self.focus_set()

        flipbook = gui.PaddedFrame(self)
        flipbook.grid(row=0, column=0, sticky='NSEW')

        left = tk.Frame(flipbook)
        left.grid(row=0, column=0, padx=(0, 12), sticky='NSEW')
        left.rowconfigure(0, weight=1)
        self.previous_button = ttk.Button(left, text='◀', width=3, takefocus=0)
        self.previous_button.grid(row=0, column=0, sticky='NSEW')
        self.previous_button['command'] = lambda event=None, direction='left': \
                                          self.flip_page(event, direction)

        right = tk.Frame(flipbook)
        right.grid(row=0, column=2, padx=(12, 0), sticky='NSEW')
        right.rowconfigure(0, weight=1)
        self.next_button = ttk.Button(right, text='▶', width=3, takefocus=0)
        self.next_button.grid(row=0, column=0, sticky='NSEW')
        self.next_button['command'] = lambda event=None, direction='right': \
                                      self.flip_page(event, direction)

        middle_color = '#e6e6e6'
        middle = tk.Frame(flipbook, bg=middle_color)
        middle.grid(row=0, column=1, sticky='NSEW')
        middle.columnconfigure(0, minsize=800)

        self.figure = Figure(figsize=(12, 7), dpi=100)
        self.figure.patch.set_facecolor(middle_color)
        self.primary = self.figure.add_subplot(111)
        self.figure.subplots_adjust(top=0.90, bottom=0.15)

        self.canvas = FigureCanvasTkAgg(self.figure, middle)
        self.canvas.draw()

        toolbar_frame = tk.Frame(middle)
        toolbar_frame.grid(row=0, column=0, sticky='NSEW')
        toolbar_frame.columnconfigure(0, weight=1)

        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.config(bg=middle_color)
        toolbar._message_label.config(bg=middle_color)
        toolbar.update()
        toolbar.grid(row=0, column=0, sticky='NSEW')

        test_frame = tk.Frame(toolbar_frame)
        test_frame.grid(row=0, column=1, sticky='NSEW')

        def show_controls():
            self.controls.update()
            self.controls.deiconify()

        controls_button = ttk.Button(toolbar_frame, text='Controls', takefocus=0,
                                     # command=self.controls_window)
                                     command=show_controls)
        controls_button.grid(row=0, column=1, sticky='E')
        global controls_image
        controls_image = gui.RenderImage(gui.ResourcePath('Assets\\controls.png'), downscale=9)
        controls_button['image'] = controls_image

        self.filename = tk.StringVar()
        filename_label = tk.Label(middle, textvar=self.filename,
                                  font=('Helvetica', 18, 'bold'),
                                  anchor='w', bg=middle_color)
        filename_label.grid(row=1, column=0, sticky='EW')

        graph_widget = self.canvas.get_tk_widget()
        graph_widget.grid(row=2, column=0, sticky='NSEW')

        left_bind = self.bind('<Left>',
                              lambda event, direction='left': self.flip_page(event, direction))
        right_bind = self.bind('<Right>',
                              lambda event, direction='right': self.flip_page(event, direction))

        self.update_arrows()
        self.update_plot()

    def update_plot(self):
        current = self.plots[self.page]
        file = self.files[self.page]
        plot = self.numbers[self.page]
        self.filename.set(f'{self.info[file].filename} - Plot {plot + 1}')

        if self.secondary:
            self.secondary.clear()
            self.secondary.axis('off')
        self.secondary = None

        self.secondary_axis = True if current.y2 else False
        if self.secondary_axis: self.secondary = self.primary.twinx()

        self.primary.clear()

        if self.secondary_axis:
            self.primary.set_zorder(1)
            self.secondary.set_zorder(100)
            self.secondary.format_coord = self._coordinates(self.secondary, self.primary,
                                                            self.secondary_axis)
        if not self.secondary_axis:
            self.primary.set_zorder(1000)
            self.primary.format_coord = self._coordinates(self.primary, None, self.secondary_axis)

        y1_colors = ['k', 'b', 'r', 'g', plot_colors['purple'], plot_colors['orange'],
                     plot_colors['brown']]
        y1_plot_colors = y1_colors[:]

        y2_colors = [plot_colors['gray'], 'c', plot_colors['pink'], plot_colors['lime'],
                     'm', plot_colors['gold'], 'y']
        y2_plot_colors = y2_colors[:]

        handles = []
        labels = []
        repeated = 0
        for y, y1 in enumerate(current.y1):

            if y % len(y1_plot_colors) == 0:
                repeated += 1
            color = y1_plot_colors[y - repeated * len(y1_plot_colors)]

            line = self.primary.plot(current.x, y1, color)
            handles.append(line[0])
            column = self.info[file].y1_columns[y]
            labels.append(current.labels[column-1])

        if self.secondary_axis:
            repeated = 0
            for y, y2 in enumerate(current.y2):

                if y % len(y2_plot_colors) == 0:
                    repeated += 1
                color = y2_plot_colors[y - repeated * len(y2_plot_colors)]

                line = self.secondary.plot(current.x, y2, color)
                handles.append(line[0])
                column = self.info[file].y2_columns[y]
                labels.append(current.labels[column-1])

        min_x = min(current.x)
        max_x = max(current.x)
        padding = (max_x - min_x) * (100/90) * (0.05)
        self.x_lower_original = min_x - padding
        self.x_upper_original = max_x + padding
        self.primary.set_xlim(self.x_lower_original, self.x_upper_original)

        self.y1_lower_original = self.primary.get_ylim()[0]
        self.y1_upper_original = self.primary.get_ylim()[1]
        if self.secondary_axis:
            self.y2_lower_original = self.secondary.get_ylim()[0]
            self.y2_upper_original = self.secondary.get_ylim()[1]

        self.primary.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)
        self.primary.minorticks_on()
        self.primary.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        self.figure.suptitle(current.title, fontweight='bold', fontsize=14)
        self.primary.set_xlabel(current.x_label)
        self.primary.set_ylabel(current.y1_label)
        if self.secondary_axis: self.secondary.set_ylabel(current.y2_label)

        lines = len(self.primary.lines)
        if self.secondary_axis: lines += len(self.secondary.lines)
        max_columns = 5
        rows = lines / max_columns
        if rows > 2: max_columns = math.ceil(lines / 2)
        self.primary.legend(
                handles = handles,
                labels = labels,
                loc = 'lower left',
                fancybox = True,
                shadow = True,
                ncol = max_columns,
                mode = 'expand',
                bbox_to_anchor = (-0.15, -0.2, 1.265, 0.1),
            )

        # Axes limits
        if current.x_lower: self.primary.set_xlim(left=current.x_lower)
        if current.x_upper: self.primary.set_xlim(right=current.x_upper)
        if current.y1_lower: self.primary.set_ylim(bottom=current.y1_lower)
        if current.y1_upper: self.primary.set_ylim(top=current.y1_upper)
        if current.y2_lower: self.secondary.set_ylim(bottom=current.y2_lower)
        if current.y2_upper: self.secondary.set_ylim(top=current.y2_upper)

        # Background selection
        if current.background.get() == 'Tactair':
            image = plt.imread(gui.ResourcePath('Assets\\tactair.bmp'))
            x_low, x_high = self.primary.get_xlim()
            y_low, y_high = self.primary.get_ylim()
            self.primary.imshow(image, extent=[x_low, x_high, y_low, y_high], aspect='auto')
        elif current.background.get() == 'Custom':
            image = plt.imread(gui.ResourcePath(current.background_path))
            x_low, x_high = self.primary.get_xlim()
            y_low, y_high = self.primary.get_ylim()
            self.primary.imshow(image, extent=[x_low, x_high, y_low, y_high], aspect='auto')

        # Tolerance Bands
        if self.band_controls:
            for p, plus in enumerate(self.band_controls.plus_bands):
                if not plus: continue
                elif plus[0] == 'primary':
                    self.primary.plot(current.x, plus[1], plot_colors[current.color[p]],
                                      linestyle='dashed')
                    # self.primary.plot(current.x, plus[1], 'c--')
                elif plus[0] == 'secondary':
                    self.secondary.plot(current.x, plus[1], plot_colors[current.color[p]],
                                      linestyle='dashed')
                    # self.secondary.plot(current.x, plus[1], 'c--')
            for m, minus in enumerate(self.band_controls.minus_bands):
                if not minus: continue
                elif minus[0] == 'primary':
                    self.primary.plot(current.x, minus[1], plot_colors[current.color[m]],
                                      linestyle='dashed')
                    # self.primary.plot(current.x, minus[1], 'c--')
                elif minus[0] == 'secondary':
                    self.secondary.plot(current.x, minus[1], plot_colors[current.color[m]],
                                      linestyle='dashed')
                    # self.secondary.plot(current.x, minus[1], 'c--')

        self.canvas.draw()

        if not self.controls:
            self.controls_window()
            self.controls.withdraw()

    def update_arrows(self):
        if self.page == 0:
            self.previous_button.config(state='disabled')
        if self.page == self.pages:
            self.next_button.config(state='disabled')
        if 0 < self.page < self.pages:
            self.previous_button.config(state='normal')
            self.next_button.config(state='normal')

    def flip_page(self, event, direction):
        destination = (self.page + 1) if direction == 'right' else (self.page - 1)
        if destination in range(self.pages + 1):
            self.page += 1 if direction == 'right' else -1
            self.refresh_controls()
            self.update_arrows()
            self.update_plot()
            self.refresh_controls()
        return ('break')

    def _coordinates(self, current, other, secondary):
        # 'current' and 'other' are axes
        if secondary:
            def format_coord(x, y):
                # x, y are data coordinates
                # Convert to display coordinates
                display_coord = current.transData.transform((x,y))
                inv = other.transData.inverted()
                # convert back to data coords with respect to ax
                ax_coord = inv.transform(display_coord)
                coords = [ax_coord, (x, y)]
                return ('Primary: {:<}  |  Secondary: {:<}'
                            .format(*['({:.3f}, {:.3f})'.format(x, y) for x,y in coords]))
        elif not secondary:
            def format_coord(x, y):
                coords = [(x, y)]
                return ('Primary: {:<}'
                            .format(*['({:.3f}, {:.3f})'.format(x, y) for x,y in coords]))
        return format_coord

    def controls_window(self):

        if self.controls: return

        def custom_background(event=None):
            before = self.background_choice.get()
            current = self.plots[self.page]
            if self.background_choice.get() == 'Custom':
                path = fd.askopenfilename(title='Select the background image')
                if path:
                    current.background_path = path
                else:
                    current.background_path = None
                    self.background_choice.set('None')
            else: current.background_path = None

        current = self.plots[self.page]

        self.controls = tk.Toplevel(self)
        self.controls.title('Controls')
        self.controls.columnconfigure(0, weight=1)
        self.controls.rowconfigure(0, weight=1)
        self.controls.protocol("WM_DELETE_WINDOW", lambda: self.controls.withdraw())

        primary = gui.PaddedFrame(self.controls)
        primary.grid(row=0, column=0, sticky='NSEW')
        primary.columnconfigure(0, weight=1)
        primary.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(primary, takefocus=0)
        notebook.grid(row=0, column=0, sticky='NSEW')

        # figure = gui.ScrollableTab(notebook, 'Figure')
        # appearance = gui.ScrollableTab(notebook, 'Appearance')
        # analysis = gui.ScrollableTab(notebook, 'Analysis')
        # annotations = gui.ScrollableTab(notebook, 'Annotations')
        # figure = gui.ScrollableTab(notebook, 'Figure', cwidth=350)
        # appearance = gui.ScrollableTab(notebook, 'Appearance', cwidth=350)
        # analysis = gui.ScrollableTab(notebook, 'Analysis', cwidth=350)
        # annotations = gui.ScrollableTab(notebook, 'Annotations', cwidth=350)
        figure = gui.ScrollableTab(notebook, 'Figure', cheight=400, cwidth=400)
        appearance = gui.ScrollableTab(notebook, 'Appearance', cheight=400, cwidth=400)
        analysis = gui.ScrollableTab(notebook, 'Analysis', cheight=400, cwidth=400)
        annotations = gui.ScrollableTab(notebook, 'Annotations', cheight=400, cwidth=400)

        gui.Separator(self.controls).grid(row=1, column=0, sticky='NSEW')

        secondary = gui.PaddedFrame(self.controls)
        secondary.grid(row=2, column=0, sticky='NSEW')
        secondary.columnconfigure(0, weight=1)

        update_button = ttk.Button(secondary, text='Update', command=self.update_controls)
        update_button.grid(row=0, column=0, sticky='E')

        # Start of Figure tab

        limits = gui.PaddedFrame(figure)
        limits.grid(row=0, column=0, sticky='NSEW')
        limits.columnconfigure(0, weight=1)
        limits.columnconfigure(1, weight=1)

        LIMITS_PADDING = 10

        x_lower_label = tk.Label(limits, text='x-lower:')
        x_lower_label.grid(row=0, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        self.x_lower_entry = ttk.Entry(limits, width=20)
        self.x_lower_entry.grid(row=1, column=0, padx=LIMITS_PADDING, sticky='NSEW')

        x_upper_label = tk.Label(limits, text='x-upper:')
        x_upper_label.grid(row=0, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        self.x_upper_entry = ttk.Entry(limits, width=20)
        self.x_upper_entry.grid(row=1, column=1, padx=LIMITS_PADDING, sticky='NSEW')

        gui.Space(limits, row=2, column=0, columnspan=2)

        y1_lower_label = tk.Label(limits, text='y1-lower:')
        y1_lower_label.grid(row=3, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        self.y1_lower_entry = ttk.Entry(limits, width=20)
        self.y1_lower_entry.grid(row=4, column=0, padx=LIMITS_PADDING, sticky='NSEW')

        y1_upper_label = tk.Label(limits, text='y1-upper:')
        y1_upper_label.grid(row=3, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        self.y1_upper_entry = ttk.Entry(limits, width=20)
        self.y1_upper_entry.grid(row=4, column=1, padx=LIMITS_PADDING, sticky='NSEW')

        gui.Space(limits, row=5, column=0, columnspan=2)

        y2_lower_label = tk.Label(limits, text='y2_lower:')
        y2_lower_label.grid(row=6, column=0, padx=LIMITS_PADDING, sticky='NSEW')
        self.y2_lower_entry = ttk.Entry(limits, width=20)
        self.y2_lower_entry.grid(row=7, column=0, padx=LIMITS_PADDING, sticky='NSEW')

        y2_upper_label = tk.Label(limits, text='y2_upper:')
        y2_upper_label.grid(row=6, column=1, padx=LIMITS_PADDING, sticky='NSEW')
        self.y2_upper_entry = ttk.Entry(limits, width=20)
        self.y2_upper_entry.grid(row=7, column=1, padx=LIMITS_PADDING, sticky='NSEW')

        # Start of Appearance tab
        background = gui.PaddedFrame(appearance)
        background.grid(row=0, column=0, sticky='NSEW')
        background.columnconfigure(0, weight=1)
        background.columnconfigure(1, weight=1)

        background_label = tk.Label(background, text='Background:')
        background_label.grid(row=0, column=0, padx=(0, 10), sticky='E')

        self.background_choice = tk.StringVar()
        background_combo = ttk.Combobox(background, width=20, state='readonly',
                                        textvariable=self.background_choice)
        background_combo.grid(row=0, column=1, padx=(10, 0), sticky='W')
        background_combo['values'] = ['None', 'Tactair', 'Young & Franklin', 'Custom']
        background_combo.bind('<<ComboboxSelected>>', custom_background)

        # Start of Analysis tab

        self.tolerance_bands = gui.PaddedFrame(analysis)
        self.tolerance_bands.grid(row=0, column=0, sticky='NSEW')
        self.tolerance_bands.columnconfigure(0, weight=1)

        # End of controls

        self.refresh_controls()

        self.controls.bind('<Return>', self.update_controls)

    def refresh_controls(self):

        if not self.controls: return

        current = self.plots[self.page]

        # Axes limits
        def axis_entry(entry, value, original):
            entry.delete(0, 'end')
            entry.insert(0, value if value else original)
        axis_entry(self.x_lower_entry, current.x_lower, self.x_lower_original)
        axis_entry(self.x_upper_entry, current.x_upper, self.x_upper_original)
        axis_entry(self.y1_lower_entry, current.y1_lower, self.y1_lower_original)
        axis_entry(self.y1_upper_entry, current.y1_upper, self.y1_upper_original)
        if self.secondary_axis:
            self.y2_lower_entry['state'] = 'normal'
            axis_entry(self.y2_lower_entry, current.y2_lower, self.y2_lower_original)
            self.y2_upper_entry['state'] = 'normal'
            axis_entry(self.y2_upper_entry, current.y2_upper, self.y2_upper_original)
        else:
            self.y2_lower_entry.delete(0, 'end')
            self.y2_lower_entry['state'] = 'disabled'
            self.y2_upper_entry.delete(0, 'end')
            self.y2_upper_entry['state'] = 'disabled'

        # Background selection
        self.background_choice.set(current.background.get())

        # Tolerance bands
        if self.band_controls: self.band_controls.grid_forget()
        self.band_controls = current.bands
        self.band_controls.setup(self.tolerance_bands)
        self.band_controls.grid(row=0, column=0, sticky='NSEW')

        if current.series and current.minus_tolerance and current.plus_tolerance and current.lag:
            longest = len(max(current.series, current.minus_tolerance,
                              current.plus_tolerance, current.lag))
            self.band_controls.recreate(rows=longest)
        self.band_controls.series = current.series
        self.band_controls.minus_tolerance = current.minus_tolerance
        self.band_controls.plus_tolerance = current.plus_tolerance
        self.band_controls.lag = current.lag
        self.band_controls.color = current.color

        values = []
        for column in current.y1_columns:
            values.append(current.labels[column-1])
        for column in current.y2_columns:
            values.append(current.labels[column-1])
        self.band_controls.update_series(values)

        # self.
        # for entry in self.band_controls.series_combos:
        #     values = []
        #     for column in current.y1_columns:
        #         values.append(current.labels[column-1])
        #     for column in current.y2_columns:
        #         values.append(current.labels[column-1])
        #     # entry['state'] = 'normal'
        #     entry['values'] = values
        #     # entry['state'] = 'readonly'

    def update_controls(self, event=None):
        current = self.plots[self.page]

        # Axes limits
        def update_axis(entry, original):
            return float(entry.get()) if entry.get() else float(original)

        current.x_lower = update_axis(self.x_lower_entry, self.x_lower_original)
        current.x_upper = update_axis(self.x_upper_entry, self.x_upper_original)
        current.y1_lower = update_axis(self.y1_lower_entry, self.y1_lower_original)
        current.y1_upper = update_axis(self.y1_upper_entry, self.y1_upper_original)
        if self.secondary_axis:
            current.y2_lower = update_axis(self.y2_lower_entry, self.y2_lower_original)
            current.y2_upper = update_axis(self.y2_upper_entry, self.y2_upper_original)

        # Background selection
        current.background.set(self.background_choice.get())

        # Tolerance bands
        current.series = self.band_controls.series
        current.minus_tolerance = self.band_controls.minus_tolerance
        current.plus_tolerance = self.band_controls.plus_tolerance
        current.lag = self.band_controls.lag
        current.color = self.band_controls.color
        self.band_controls.calculate(current)

        self.update_plot()
        self.refresh_controls()
















































class ToleranceBands(tk.Frame):

    def __init__(self):

        # self.plus_backup = []
        # self.minus_backup = []

        self.plus_bands = []
        self.minus_bands = []

        self.reset()

    def setup(self, master):

        tk.Frame.__init__(self, master=master)
        self.columnconfigure(0, weight=1)

        controls = tk.Frame(self)
        controls.grid(row=0, column=0, sticky='NSEW')
        controls.columnconfigure(0, weight=1)

        title = tk.Label(controls, text='Tolerance Bands')
        title.grid(row=0, column=0, sticky='W')

        add_button = ttk.Button(controls, text='+', width=3, command=self.add_band)
        add_button.grid(row=0, column=1)

        delete_button = ttk.Button(controls, text='-', width=3, command=self.delete_band)
        delete_button.grid(row=0, column=2)

    def reset(self):
        self.count = 0
        self.bands = []

        self.series_choices = []
        self.color_choices = []

        self.series_combos = []
        self.minus_tolerance_entries = []
        self.plus_tolerance_entries = []
        self.lag_entries = []
        self.color_combos = []

        self.values = None

        # self.plus_backup = self.plus_bands
        # self.minus_backup = self.minus_bands

        # print(f'Minus backup:\n\t\t\t{self.minus_backup}')

        self.plus_bands = []
        self.minus_bands = []

    def recreate(self, rows):
        self.minus_backup = self.minus_bands
        self.plus_backup = self.plus_bands
        self.reset()
        for row in range(rows):
            self.add_band(recreate=row)
            # self.plus_bands.append(None)
            # self.minus_bands.append(None)
        self.minus_bands = self.minus_backup
        self.plus_bands = self.plus_backup

        # print(self.minus_bands)

    def add_band(self, recreate=None):

        PADDING = 2

        frame = tk.Frame(self)
        frame.grid(row=self.count+1 if not recreate else recreate+1, column=0, pady=(10, 0))

        series_label = ttk.Label(frame, text='series:')
        series_label.grid(row=0, column=0, padx=PADDING)

        plus_tolerance_label = ttk.Label(frame, text='+tol.:')
        plus_tolerance_label.grid(row=0, column=1, padx=PADDING)

        minus_tolerance_label = ttk.Label(frame, text='-tol.:')
        minus_tolerance_label.grid(row=0, column=2, padx=PADDING)

        lag_label = ttk.Label(frame, text='lag:')
        lag_label.grid(row=0, column=3, padx=PADDING)

        color_label = ttk.Label(frame, text='color:')
        color_label.grid(row=0, column=4, padx=PADDING)

        series_choice = tk.StringVar()
        series_combo = ttk.Combobox(frame, width=14, state='readonly',
                                    textvariable=series_choice,
                                    postcommand=self.update_entries)
        series_combo.grid(row=1, column=0, padx=PADDING)
        self.series_choices.append(series_choice)
        self.series_combos.append(series_combo)

        plus_tolerance_entry = ttk.Entry(frame, width=8)
        plus_tolerance_entry.grid(row=1, column=1, padx=PADDING)
        self.plus_tolerance_entries.append(plus_tolerance_entry)

        minus_tolerance_entry = ttk.Entry(frame, width=8)
        minus_tolerance_entry.grid(row=1, column=2, padx=PADDING)
        self.minus_tolerance_entries.append(minus_tolerance_entry)

        lag_entry = ttk.Entry(frame, width=8)
        lag_entry.grid(row=1, column=3, padx=PADDING)
        self.lag_entries.append(lag_entry)

        color_choice = tk.StringVar()
        color_choice.set(random.choice(list(plot_colors.keys())))
        color_combo = ttk.Combobox(frame, textvariable=color_choice,
                                   width=8, state='readonly')
        color_combo['values'] = list(plot_colors.keys())
        color_combo.grid(row=1, column=4, padx=PADDING)
        self.color_choices.append(color_choice)
        self.color_combos.append(color_combo)

        # self.plus_bands.append(None)
        # self.minus_bands.append(None)

        # if recreate:
        #     self.plus_bands = self.plus_backup
        #     self.minus_bands = self.minus_backup
        # else:
        #     self.plus_bands.append(None)
        #     self.minus_bands.append(None)

        if not recreate:
            self.plus_bands.append(None)
            self.minus_bands.append(None)

        self.count += 1
        self.bands.append(frame)

    def delete_band(self):
        if len(self.bands) == 0: return
        self.bands[-1].destroy()
        del(self.bands[-1])

        del(self.series_combos[-1])
        del(self.minus_tolerance_entries[-1])
        del(self.plus_tolerance_entries[-1])
        del(self.lag_entries[-1])
        del(self.color_combos[-1])

        del(self.minus_bands[-1])
        del(self.plus_bands[-1])

        # print(len(self.series_combos))
        # print(len(self.minus_bands))

        self.count -= 1

    def update_series(self, values):
        self.values = values

    def update_entries(self):
        for entry in self.series_combos:
            entry['values'] = self.values

    def calculate(self, plot):

        def BandData(iterator, which):
            series = self.series_combos[iterator].get()

            def get_value(entry):
                return float(entry.get()) if entry.get() else 0

            # MINUS_TOLERANCE = float(self.minus_tolerance_entries[iterator].get())
            # PLUS_TOLERANCE = float(self.plus_tolerance_entries[iterator].get())
            # LAG = float(self.lag_entries[iterator].get())
            MINUS_TOLERANCE = get_value(self.minus_tolerance_entries[iterator])
            PLUS_TOLERANCE = get_value(self.plus_tolerance_entries[iterator])
            LAG = get_value(self.lag_entries[iterator])

            for l, label in enumerate(plot.labels):
                if label == series:
                    index = l

            if index + 1 in plot.y1_columns:
                axis = 'primary'
                position = plot.y1_columns.index(index + 1)
            else:
                axis = 'secondary'
                position = plot.y2_columns.index(index + 1)

            x = plot.x
            if axis == 'primary':
                y = plot.y1[position]
            elif axis == 'secondary':
                y = plot.y2[position]

            # Maybe take average distance between each point in x instead?
            resolution = x[1] - x[0]
            lookback = round(LAG / resolution)

            band = []
            for i, c in enumerate(y):
                if i >= lookback:
                    if which == '+':
                        # Get the maximum value in the lookback range and add tolerance
                        maximum = max(y.loc[i-lookback:i+1])
                        toleranced = maximum + PLUS_TOLERANCE
                    elif which == '-':
                        # Get the minimum value in the lookback range and subtract tolerance
                        minimum = min(y.loc[i-lookback:i+1])
                        toleranced = minimum - MINUS_TOLERANCE
                    band.append(toleranced)
                else:
                    # Don't want to plot any values before a lookback can be done
                    band.append(None)

            return (axis, band)

        for i in range(len(self.series_combos)):
            # self.plus_bands.append(BandData(i, which='+'))
            # self.minus_bands.append(BandData(i, which='-'))
            self.plus_bands[i] = BandData(i, which='+')
            self.minus_bands[i] = BandData(i, which='-')

    @property
    def series(self):
        return [combo.get() for combo in self.series_combos]

    @series.setter
    def series(self, series):
        if series:
            for i in range(len(series)):
                self.series_choices[i].set(series[i] if series[i] else '')

    @property
    def minus_tolerance(self):
        return [entry.get() for entry in self.minus_tolerance_entries]

    @minus_tolerance.setter
    def minus_tolerance(self, tolerances):
        if tolerances:
            for i in range(len(tolerances)):
                self.minus_tolerance_entries[i].delete(0, 'end')
                self.minus_tolerance_entries[i].insert(0, tolerances[i] if tolerances[i] else '')

    @property
    def plus_tolerance(self):
        return [entry.get() for entry in self.plus_tolerance_entries]

    @plus_tolerance.setter
    def plus_tolerance(self, tolerances):
        if tolerances:
            for i in range(len(tolerances)):
                self.plus_tolerance_entries[i].delete(0, 'end')
                self.plus_tolerance_entries[i].insert(0, tolerances[i] if tolerances[i] else '')

    @property
    def lag(self):
        return [entry.get() for entry in self.lag_entries]

    @lag.setter
    def lag(self, lags):
        if lags:
            for i in range(len(lags)):
                self.lag_entries[i].delete(0, 'end')
                self.lag_entries[i].insert(0, lags[i] if lags[i] else '')

    @property
    def color(self):
        return [combo.get() for combo in self.color_combos]

    @color.setter
    def color(self, colors):
        if colors:
            for i in range(len(colors)):
                self.color_choices[i].set(colors[i] if colors[i] else '')









































class File(gui.ScrollableTab):

    def __init__(self, notebook, filepath):
        self.filepath = filepath
        self.filename = self.filepath.split('/')[-1]
        gui.ScrollableTab.__init__(self, notebook, self.filename, cwidth=571, cheight=252)
        self._count = 0
        self._rows = []
        self._titles = []
        self._x_columns = []
        self._y1_columns = []
        self._y2_columns = []
        self._x_labels = []
        self._y1_labels = []
        self._y2_labels = []
        self.plots = []

        controls = tk.Frame(self)
        controls.grid(row=0, column=0, pady=20, sticky='NSEW')
        for column in [0, 3, 6, 9]:
            controls.columnconfigure(column, weight=1)

        data_row_label = tk.Label(controls, text='Data start row:')
        data_row_label.grid(row=0, column=1, sticky='NSEW')

        self.data_row_entry = ttk.Entry(controls, width=10)
        self.data_row_entry.grid(row=0, column=2, padx=5, sticky='NSEW')

        label_row_label = tk.Label(controls, text='Label row:')
        label_row_label.grid(row=0, column=4, sticky='NSEW')

        self.label_row_entry = ttk.Entry(controls, width=10)
        self.label_row_entry.grid(row=0, column=5, padx=5, sticky='NSEW')

        unit_row_label = tk.Label(controls, text='Unit row:')
        unit_row_label.grid(row=0, column=7, sticky='NSEW')

        self.unit_row_entry = ttk.Entry(controls, width=10)
        self.unit_row_entry.grid(row=0, column=8, padx=5, sticky='NSEW')

        self.data_row_entry.bind('<FocusIn>', self._scroll_into_view)
        self.label_row_entry.bind('<FocusIn>', self._scroll_into_view)
        self.unit_row_entry.bind('<FocusIn>', self._scroll_into_view)

        self.add_row()

    def add_row(self):

        MARGINS = 8
        TOOLS = 2
        PADDING = 5

        frame = tk.LabelFrame(self, text=f'Plot {self._count + 1}')
        frame.grid(row=self._count + 1, column=0, padx=MARGINS, pady=(0, MARGINS*2), sticky='NSEW')
        frame.columnconfigure(0, weight=1)

        inner = tk.Frame(frame)
        inner.grid(row=0, column=0, padx=MARGINS*2, pady=MARGINS*2, sticky='NSEW')
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(2, weight=1)
        inner.columnconfigure(3, weight=10)

        tools = tk.Frame(inner)
        tools.grid(row=0, column=0, columnspan=4, padx=PADDING, sticky='NSEW')
        tools.columnconfigure(1, weight=1)

        title_label = tk.Label(tools, text='Title:')
        title_label.grid(row=0, column=0, sticky='NSEW')

        title_entry = ttk.Entry(tools)
        title_entry.grid(row=0, column=1, padx=PADDING, sticky='NSEW')
        self._titles.append(title_entry)

        copy_button = ttk.Button(tools, takefocus=0, width=3, text='C')
        copy_button['command'] = lambda ID=self._count: self.copy(ID)
        copy_button.grid(row=0, column=2, padx=TOOLS, sticky='NSEW')

        paste_button = ttk.Button(tools, takefocus=0, width=3, text='P')
        paste_button['command'] = lambda ID=self._count: self.paste(ID)
        paste_button.grid(row=0, column=3, padx=TOOLS, sticky='NSEW')

        clear_button = ttk.Button(tools, takefocus=0, width=3, text='X')
        clear_button.grid(row=0, column=4, padx=TOOLS, sticky='NSEW')

        gui.Space(inner, row=1, column=0, columnspan=4, padding=PADDING)

        x_column_label = tk.Label(inner, text='x column:')
        x_column_label.grid(row=2, column=0, padx=PADDING, sticky='NSEW')

        x_column_entry = ttk.Entry(inner, width=10)
        x_column_entry.grid(row=3, column=0, padx=PADDING, sticky='NSEW')
        self._x_columns.append(x_column_entry)

        y1_column_label = tk.Label(inner, text='y1 columns:')
        y1_column_label.grid(row=2, column=1, padx=PADDING, sticky='NSEW')

        y1_column_entry = ttk.Entry(inner, width=10)
        y1_column_entry.grid(row=3, column=1, padx=PADDING, sticky='NSEW')
        self._y1_columns.append(y1_column_entry)

        y2_column_label = tk.Label(inner, text='y2 columns:')
        y2_column_label.grid(row=2, column=2, padx=PADDING, sticky='NSEW')

        y2_column_entry = ttk.Entry(inner, width=10)
        y2_column_entry.grid(row=3, column=2, padx=PADDING, sticky='NSEW')
        self._y2_columns.append(y2_column_entry)

        x_axis_label = tk.Label(inner, text='x axis label:')
        x_axis_label.grid(row=2, column=3, padx=PADDING, sticky='NSEW')

        x_axis_entry = ttk.Entry(inner)
        x_axis_entry.grid(row=3, column=3, padx=PADDING, sticky='NSEW')
        self._x_labels.append(x_axis_entry)

        gui.Space(inner, row=4, column=0, columnspan=4, padding=PADDING)

        y1_axis_label = tk.Label(inner, text='y1 axis label:')
        y1_axis_label.grid(row=5, column=0, columnspan=3, padx=PADDING, sticky='NSEW')

        y1_axis_entry = ttk.Entry(inner)
        y1_axis_entry.grid(row=6, column=0, columnspan=3, padx=PADDING, sticky='NSEW')
        self._y1_labels.append(y1_axis_entry)

        y2_axis_label = tk.Label(inner, text='y2 axis label:')
        y2_axis_label.grid(row=5, column=3, padx=PADDING, sticky='NSEW')

        y2_axis_entry = ttk.Entry(inner)
        y2_axis_entry.grid(row=6, column=3, padx=PADDING, sticky='NSEW')
        self._y2_labels.append(y2_axis_entry)

        title_entry.bind('<FocusIn>', self._scroll_into_view)
        x_column_entry.bind('<FocusIn>', self._scroll_into_view)
        y1_column_entry.bind('<FocusIn>', self._scroll_into_view)
        y2_column_entry.bind('<FocusIn>', self._scroll_into_view)
        x_axis_entry.bind('<FocusIn>', self._scroll_into_view)
        y1_axis_entry.bind('<FocusIn>', self._scroll_into_view)
        y2_axis_entry.bind('<FocusIn>', self._scroll_into_view)

        self._count += 1
        self._rows.append(frame)
        self.add_plot()

    def delete_row(self):
        if len(self._rows) <= 1: return
        self._rows[-1].destroy()
        del(self._rows[-1])
        del(self.plots[-1])
        self._count -= 1

    def _scroll_into_view(self, event):
        widget_top = event.widget.winfo_rooty()
        widget_bottom = widget_top + event.widget.winfo_height()
        canvas_top = self.canvas.winfo_rooty()
        canvas_bottom = canvas_top + self.canvas.winfo_height()

        parent_inner = app.root.nametowidget(event.widget.winfo_parent())
        parent_outer = app.root.nametowidget(parent_inner.winfo_parent())

        MARGIN = 30
        if widget_bottom > canvas_bottom:
            delta = int(widget_bottom - canvas_bottom) + MARGIN
            self.canvas.yview_scroll(delta, 'units')
        elif widget_top < canvas_top:
            delta = int(widget_top - canvas_top) - MARGIN
            self.canvas.yview_scroll(delta, 'units')

    def copy(self, ID):
        clipboard['title'] = self._titles[ID].get()
        clipboard['x column'] = self._x_columns[ID].get()
        clipboard['y1 columns'] = self._y1_columns[ID].get()
        clipboard['y2 columns'] = self._y2_columns[ID].get()
        clipboard['x label'] = self._x_labels[ID].get()
        clipboard['y1 label'] = self._y1_labels[ID].get()
        clipboard['y2 label'] = self._y2_labels[ID].get()

    def paste(self, ID):
        self._titles[ID].insert(0, clipboard['title'])
        self._x_columns[ID].insert(0, clipboard['x column'])
        self._y1_columns[ID].insert(0, clipboard['y1 columns'])
        self._y2_columns[ID].insert(0, clipboard['y2 columns'])
        self._x_labels[ID].insert(0, clipboard['x label'])
        self._y1_labels[ID].insert(0, clipboard['y1 label'])
        self._y2_labels[ID].insert(0, clipboard['y2 label'])

    def add_plot(self):

        class Plot:

            def __init__(self):
                self.x = None
                self.y1 = None
                self.y2 = None
                self.title = None
                self.x_label = None
                self.y1_label = None
                self.y2_label = None

                self.x_lower = None
                self.x_upper = None
                self.y1_lower = None
                self.y1_upper = None
                self.y2_lower = None
                self.y2_upper = None

                self.background = tk.StringVar()
                self.background.set('None')
                self.background_path = None

                self.bands = ToleranceBands()
                self.series = None
                self.minus_tolerance = None
                self.plus_tolerance = None
                self.lag = None
                self.color = None

            def _x_data(self, x_column):
                x = self.data[self.labels[x_column-1]]
                return x

            def _y_data(self, y_columns):
                y = [self.data[self.labels[column-1]] for column in y_columns]
                return y

            def _generate(self, data, labels, x_column, y1_columns, y2_columns=None,
                          units=None):
                self.data = data
                self.labels = labels
                self.units = units

                self.x_column = x_column
                self.y1_columns = y1_columns
                self.y2_columns = y2_columns

                self.x = self._x_data(x_column)
                self.y1 = self._y_data(y1_columns)
                self.y2 = self._y_data(y2_columns) if y2_columns else None

            def _labels(self, title, x_label, y1_label, y2_label):
                self.title = title if title else None
                self.x_label = x_label if x_label else None
                self.y1_label = y1_label if y1_label else None
                self.y2_label = y2_label if y2_label else None

        plot = Plot()
        self.plots.append(plot)

    def _filetype(self, path):
        name, extension = os.path.splitext(path)
        if extension in ['.csv', '.dat']: return 'CSV'
        elif extension in ['.xls', '.xlsx', '.xlsm']: return 'Excel'
        else: raise TypeError(f'The .{extension} filetype is not supported.')

    def _labels(self, label_row):
        if self._type == 'CSV':
            labels = pd.read_csv(self.filepath, skiprows=label_row-1, nrows=1,
                                 index_col=False, header=None)
        elif self._type == 'Excel':
            labels = pd.read_excel(self.filepath, skiprows=label_row-1, nrows=1,
                                   index_col=False, header=None, encoding='latin1')
        return list(labels.values.flatten())

    def _units(self, unit_row):
        if not unit_row: return None

        if self._type == 'CSV':
            units = pd.read_csv(self.filepath, skiprows=unit_row-1, nrows=1,
                                index_col=False, header=None)
        elif self._type == 'Excel':
            units = pd.read_excel(self.filepath, skiprows=unit_row-1, nrows=1,
                                  index_col=False, header=None, encoding='latin1')
        return list(units.values.flatten())

    def _data(self, data_start_row):
        if self._type == 'CSV':
            data = pd.read_csv(self.filepath, skiprows=data_start_row-1,
                               names=self.labels, index_col=False,
                               header=None)
        elif self._type == 'Excel':
            data = pd.read_excel(self.filepath, skiprows=data_start_row-1,
                                 names=self.labels, index_col=False,
                                 header=None, encoding='latin1')
        return data

    def generate(self):

        self._type = self._filetype(self.filepath)

        self.label_row = int(self.label_row_entry.get())
        self.labels = self._labels(self.label_row)

        self.unit_row = int(self.unit_row_entry.get()) if self.unit_row_entry.get() else None
        self.units = self._units(self.unit_row)

        self.data_start_row = int(self.data_row_entry.get())
        self.data = self._data(self.data_start_row)

        for p, plot in enumerate(self.plots):
            title = self._titles[p].get()
            x_column = int(self._x_columns[p].get())
            self.y1_columns = [int(item) for item in re.findall(r'\d+', self._y1_columns[p].get())]
            self.y2_columns = [int(item) for item in re.findall(r'\d+', self._y2_columns[p].get())]
            x_label = self._x_labels[p].get()
            y1_label = self._y1_labels[p].get()
            y2_label = self._y2_labels[p].get()

            plot._generate(self.data, self.labels, x_column, self.y1_columns,
                           self.y2_columns, self.units)
            plot._labels(title, x_label, y1_label, y2_label)


PADDING = 12

app = gui.Application(padding=PADDING)
app.configure(
        title='EZPZ Plotting',
        icon=gui.ResourcePath('Assets\\icon.ico'),
        resizable=False
    )

header = gui.Header(app, logo=gui.ResourcePath('Assets\\logo.png'), downscale=10)
header.grid(row=0, column=0, sticky='NSEW')

gui.Separator(app, padding=(0, PADDING)).grid(row=1, column=0, sticky='NSEW')

browse_image = gui.RenderImage('Assets\\browse.png', downscale=9)
listbox = gui.InputField(app, quantity='multiple', appearance='list', width=80,
                         image=browse_image, command=browse)
listbox.grid(row=2, column=0, sticky='NSEW')

gui.Separator(app, padding=(0, PADDING)).grid(row=3, column=0, sticky='NSEW')

primary = tk.Frame(app)
primary.grid(row=4, column=0, sticky='NSEW')
primary.columnconfigure(0, weight=1)
primary.rowconfigure(0, minsize=278)

message = 'Please provide at least one input file.\n\nControls will appear here.'
no_input_label = tk.Label(primary, text=message)
no_input_label.grid(row=0, column=0, sticky='NSEW')

gui.Separator(app, padding=(0, PADDING)).grid(row=5, column=0, sticky='NSEW')

footer = tk.Frame(app)
footer.grid(row=6, column=0, sticky='NSEW')
footer.columnconfigure(1, weight=1)

row_controls = tk.Frame(footer)
row_controls.grid(row=0, column=0, sticky='NSEW')

plus_image = gui.RenderImage('Assets\\plus.png', downscale=9)
plus_button = ttk.Button(row_controls, takefocus=0, image=plus_image, state='disabled')
plus_button['command'] = plus_row
plus_button.grid(row=0, column=0, padx=2, sticky='NSEW')

minus_image = gui.RenderImage('Assets\\minus.png', downscale=9)
minus_button = ttk.Button(row_controls, takefocus=0, image=minus_image, state='disabled')
minus_button['command'] = minus_row
minus_button.grid(row=0, column=1, padx=2, sticky='NSEW')

plot_image = gui.RenderImage('Assets\\plot.png', downscale=9)
plot_button = ttk.Button(footer, takefocus=0, image=plot_image, state='disabled')
plot_button['command'] = plot_function
plot_button.grid(row=0, column=2, padx=2, sticky='NSEW')

menu_bar = tk.Menu(app.root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label='Load Files', command=listbox.Browse)
file_menu.add_command(label='Add File', state='disabled', command=add_file)
file_menu.add_command(label='Remove File', state='disabled', command=remove_file)
file_menu.add_separator()
file_menu.add_command(label='Save Preset', state='disabled', command=save_preset)
file_menu.add_command(label='Load Preset', command=load_preset)
file_menu.add_separator()
file_menu.add_command(label='Exit', command=lambda: app.root.destroy())
menu_bar.add_cascade(label='File', menu=file_menu)
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label='Clear Form', state='disabled', command=clear_all)
edit_menu.add_command(label='Reset Form', state='disabled', command=reset)
edit_menu.add_separator()
edit_menu.add_command(label='Paste (Selected File)', state='disabled', command=paste_file)
edit_menu.add_command(label='Paste (All Files)', state='disabled', command=paste_all)
menu_bar.add_cascade(label='Edit', menu=edit_menu)
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label='View Help')
help_menu.add_separator()
help_menu.add_command(label='About', state='disabled')
menu_bar.add_cascade(label='Help', menu=help_menu)
app.root.config(menu=menu_bar)

app.root.bind('<Return>', plot_function)

app.root.bind('<Control-minus>', minus_row)
app.root.bind('<Control-=>', plus_row)
app.root.bind('<Insert>', lambda event, direction='previous': switch_tab(event, direction)) # Insert
app.root.bind('<Prior>', lambda event, direction='next': switch_tab(event, direction)) # Page Up



def test_function():
    global inputs, files

    location = 'Presets\\preset.ini'
    preset = configobj.ConfigObj(location)

    if len(preset) == 0:
        message = 'It looks like the preset file you chose is either empty or not ' \
                  'formatted correctly. Please double check the file and try again.'
        mb.showinfo('Oops!', message)
        return

    inputs = [info['filepath'] for file, info in preset.items()]

    listbox.clear()
    listbox.field['state'] = 'normal'
    for filepath in inputs: listbox.field.insert('end', ' ' + filepath)
    listbox.field['state'] = 'disable'
    listbox.field['justify'] = 'left'

    enable()
    input_controls()

    for f, (file, info) in enumerate(preset.items()):
        if len(info) > 5:
            rows_needed = len(info) - 5
            for _ in range(rows_needed): plus_row(tab=f)

    for f, (file, info) in enumerate(preset.items()):
        files[f].data_row_entry.insert(0, info['data start'])
        files[f].label_row_entry.insert(0, info['label row'])
        files[f].unit_row_entry.insert(0, info['unit row'])
        plots = [key for key in info.keys()
                 if key not in ['filepath', 'data start', 'label row', 'unit row']]

        for p, plot in enumerate(plots):
            files[f]._titles[p].insert(0, info[plot]['title'])
            files[f]._x_columns[p].insert(0, info[plot]['x column'])
            files[f]._y1_columns[p].insert(0, info[plot]['y1 columns'])
            files[f]._y2_columns[p].insert(0, info[plot]['y2 columns'])
            files[f]._x_labels[p].insert(0, info[plot]['x label'])
            files[f]._y1_labels[p].insert(0, info[plot]['y1 label'])
            files[f]._y2_labels[p].insert(0, info[plot]['y2 label'])

    plot_function()
app.after(100, test_function)



app.mainloop()