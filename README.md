# Ambiguity Function Computation for Pulse Frequency Radars

## (C) Tooring Analytics, 2015

A python module for computing the Ambiguity Function for analyzing radar signals, as outlined in 'Radar Signals' by Levanon & Mozeson.

Requirements:
--------------

- distribute>=0.7.3
- numpy>=1.9.1
- scipy>=0.15.1
- If using a virtualenv, [any suitable display backend for matplotlib](http://stackoverflow.com/questions/9054718/matplotlib-doesnt-display-graph-in-virtualenv "Stackoverflow discussion on this.")
- matplotlib>=1.4.2


Please ensure the above dependencies are met before running this script

Numpy, Scipy and matplotlib can be installed by:

```
pip install numpy scipy matplotlib
```

Or, by using the bundled requirements.txt:

```
pip install --upgrade --force-reinstall -r requirements.txt
```

Usage:
------

This is the function signature for the 'ambiguity' method:

```
def ambiguity(u_basic=DEFAULT_SIGNAL,
              fcode=True,
              f_basic=None,
              F=0,
              K=0,
              T=0,
              N=0,
              sr=0,
              plot_title="",
              plot1_file=None,
              plot2_file=None,
              plot_format="svg",
              plot_mesh=True,
              elev=50,
              azim=-135,
              figsize=None,
              plot_grid=False,
              ):
    """ Compute Ambiguity & generate Plots for given input parameters
    Params:
    -------
    u_basic: numpy.ndarray or array-like. Input signal.
    fcode: bool True if frequency coding allowed, false otherwise
    f_basic: numpy.ndarray or array-like. Frequency coding in
    units of 1/tb (row vector of same length)
    F: int. Maximal Doppler shift for ambiguity in plot
    [in units of 1/Mtb] (e.g. 1)
    K: int. Number of Doppler grid points for calculation (e.g. 100)
    T: float. Maximal Delay for ambiguity plot [in units of Mtb]
    N: int. Number of delay grid points on each side (e.g. 100)
    sr: int/float. Over sampling ratio (>=1) (e.g. 10)
    plot1_file: str. Name of file where first plot will be stored.
    If 'None', pops up an itneractive window to display this plot.
    plot2_file: str. Name of file where second plot will be stored.
    If 'None', pops up an itneractive window to display this plot.
    plot_format: str. Output format for plot. (e.g. 'svg', 'png', 'pdf'
     etc. Check matplotlib docs for supported formats.)
    plot_mesh: bool. If True (default), plots a mesh, if False plots a
    surface.
    elev: float.(default=50) Elevation for 3-D plot viewpoint.
    azim: float.(default=-135) Azimuth in degrees for 3-D plot viewpoint.
    figsize: figure size (width, height) in inches.
    plot_grid: bool (default=False) to control grid lines in 2d-plot.

    Returns:
    --------
    (delay, freq, a): 3-tuple of array_like's, where delay, freq and a
    are the time, frequence and amplitude values.
    """

```

To use, first import the ambiguity module as follows:

```
from ambiguity import ambiguity
```

Then, set up the input parameters for calling the method,
for e.g.:

```
import numpy as np

u_basic = np.ones((1, 51))
fcode =  True
f_basic = np.dot(0.0031,
                 np.array(np.arange(-25, 26)))
F = 6
K = 360
T = 1.1
N = 360
sr = 10
plot_title = 'LFM'       # The title to print in the plots
plot1_file = 'fig_1.png' #Optional
plot2_file = 'fig_2.png' #Optional
plot_format = 'png'      #Optional
plot_mesh = True         #Optional
```

Now call the ambiguity function with the above parameters:

```
ambiguity(u_basic,
          fcode,
          f_basic,
          F,
          K,
          T,
          N,
          sr,
          plot_title,
          plot1_file,
          plot2_file,
          plot_format,
          plot_mesh)
```

if plot1_file and plot2_file are None or not given, the function
will attempt to pop up a matplotlib interactive display to show the plot.

You can use the elev and azim optional parameters to set up the initial
view point in the 3-D plot. The plot_mesh boolean argument,
(default: True), decides whether a mesh grid or a colormapped surface
is plotted in the 3-D plot.
