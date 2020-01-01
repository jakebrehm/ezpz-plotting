<p align="center">
  <img src="https://github.com/jakebrehm/ezpz-plotting/blob/master/Assets/logo.png" width="558" height="126" alt="EZPZ Plotting Logo"/>
</p>

---

**EZPZ Plotting** is a program that allows the user to easily create, view, and manipulate multiple plots from multiple files at once.

# Main features

- Takes multiple data files as input, and is able to make multiple plots from each file
- Effortlessly "flip" through the *flipbook*, where each page is a different plot
- Manipulate each plot individually, e.g. adjust axes limits or add a background
- Preset files allow you to continue where you left off
- Perform more complex data analysis using *special* plot types

# How to get it

Clone this repository via the following command:

```
git clone https://github.com/jakebrehm/ezpz-plotting.git
```

Then, run *main.py*. Alternatively, download and run *EZPZ Plotting.exe*.

## Support

Currently, *only Windows is supported*. Support for other operating systems will be added in the future.

## Dependencies

- [lemons](https://github.com/jakebrehm/lemons)
- [matplotlib](https://github.com/matplotlib/matplotlib)
- [pandas](https://github.com/pandas-dev/pandas)
- [configobj](https://github.com/DiffSK/configobj)

The **lemons** package is my own creation, and it is mainly used for GUI-related purposes. **Matplotlib** is used for plotting, **pandas** is used for data parsing, and **configobj** is used for saving and loading of presets.

# How to use it

Using **EZPZ Plotting** is easy! First, you need to pass it some data files.

## Loading data files

To load data files into **EZPZ Plotting**, you have two options:
1. Press the large `Browse...` button.
2. From the menu bar, select either `File > Load Files` or `File > Add File`.

Pressing the `Browse...` button or selecting `File > Load Files` will allow you to load multiple data files. To do this, hold <kbd>Shift</kbd> or <kbd>Ctrl</kbd> when choosing your files in the file dialog. Please note that these functions will **erase your previous inputs**.

Alternatively, selecting `File > Add File` will only let you add a single file. This feature is primarily used when you already have files loaded and you just want to add one more.

<p align="center">
  <img src="https://raw.githubusercontent.com/jakebrehm/ezpz-plotting/master/img/loading_files.gif"
  alt="Loading Files into EZPZ Plotting"/>
</p>

## Providing plot information

Each file that you loaded will now have its own tab. At the top of each tab, there are three fields, two of which are required.

- **Data start row** is required, and is the row number that your data actually starts on; e.g. if your data file has a header that is three rows long, and the data immediately follows on row four, you would enter a value of *4* in this field.
- **Label row** is also required, and is the row number of your data's column labels.
- **Unit row** is optional and is the row number of your data's units.

Now, you must tell the program what you want to plot. Each plot will be held within its own frame and given a number. *Plot 1* was automatically added for you when you loaded the file. Each plot has seven fields, but only two of them are required.

- **Title** is optional, and is the title that will appear above the plot.
- **x column** is required, and is the column number that you want to be plotted on the x-axis.
- **y1 columns** is required, and is the column number(s) that you want to be plotted on the primary axis.
- **y2 columns** is optional, and is the column number(s) that you want to be plotted on the secondary axis.
- **x axis label** is optional, and is the label of the x-axis that will appear at the bottom of the plot.
- **y1 axis label** is optional, and is the label of the primary axis that will appear to the left of the plot.
- **y2 axis label** is optional, and is the label of the secondary axis that will appear to the right of the plot.

To specify more than one column in the *y1 columns* and *y2 columns* fields, separate the column numbers by any character other than a number. Conventionally, semicolons are used, e.g. `2;3;4`.

<p align="center">
  <img src="https://raw.githubusercontent.com/jakebrehm/ezpz-plotting/master/img/plot_information.gif"
  alt="Specifying Plot Information"/>
</p>

## Adding or removing plots

To make another plot for the currently selected data file, press the `+` or `-` buttons at the bottom left of the program.

<p align="center">
  <img src="https://raw.githubusercontent.com/jakebrehm/ezpz-plotting/master/img/adding_removing_plots.gif"
  alt="Adding and Removing Plots"/>
</p>

This will either add or remove a plot **from the current tab**.

## Adding or removing files

To add another file after loading the initial file(s), select `File > Add File` and choose the data file to add.

To remove a file, select `File > Remove File`, which will remove the currently selected tab/data file.

<p align="center">
  <img src="https://raw.githubusercontent.com/jakebrehm/ezpz-plotting/master/img/adding_removing_files.gif"
  alt="Adding and Removing Files"/>
</p>

## Plotting and navigating the flipbook

When you are ready to generate your plots, press the `Plot` button in the bottom right of the program. The flipbook will open and show your first plot.

If you made more than one plot, you can "flip" between them by pressing the left or right arrows buttons on either side of the flipbook, or you can press the <kbd>←</kbd> or <kbd>→</kbd> arrow keys on your keyboard.

<p align="center">
  <img src="https://raw.githubusercontent.com/jakebrehm/ezpz-plotting/master/img/using_the_flipbook.gif"
  alt="Using the Flipbook"/>
</p>

## Manipulating the plots

To manipulate features of each plot, such as its axis limits or its background, open the controls window by pressing the `Controls` button at the top right of the flipbook.

The controls window will appear, and it holds multiple tabs, each holding their own settings. Adjust to your heart's content and then press the `Update` button. The plot will update, taking into account the changes that you requested.

Each plot has its own "memory"/settings. You can close and reopen the flipbook and these changes will remain intact.

<p align="center">
  <img src="https://raw.githubusercontent.com/jakebrehm/ezpz-plotting/master/img/controls_window.gif"
  alt="Using the Controls Window"/>
</p>

## Special plots

Special plots are extra plot types added upon request. They are tailored to a specific type of data file and perform appropriate calculations and analysis.

**Do not attempt** to use these plots if you don't know what they are.

# Ideas for future changes
- Update the help window
- Add support for other operating systems
- Refactor the code now that it has been changed heavily
- Keep settings for each plot in preset files
- Make the executable file smaller

---

# Authors
- **Jake Brehm** - *Initial Work* - [Email](mailto:mail@jakebrehm.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)