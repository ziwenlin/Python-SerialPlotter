import tkinter as tk
from typing import List

from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class GraphFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Create figure so graphs can be plotted
        self.figure = Figure(figsize=(9, 5))

        # Create a canvas where the figure can be displayed
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Create the toolbar and pack it (yes canvas is no typo)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Create the plots and lines
        self.plot: Axes = self.figure.add_subplot()
        self.lines: List[Line2D] = []
