import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
from typing import Dict

UPDATE_INTERVAL = 20


class GraphBase:

    def __init__(self, root: tk.Widget):
        self.figure = Figure(figsize=(9, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, root)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.root = root
        self.draw()
        self.plot: Axes = self.figure.add_subplot()
        self.lines: Dict[str, Line2D] = {}

    def update(self, data: Dict[str, list]):
        for key, y_data in data.items():
            length = len(y_data)
            x_data = [x for x in range(length)]
            if key not in self.lines:
                lines = self.plot.plot(x_data, y_data, linewidth=1)
                self.lines.update({key: lines[0]})
            self.lines.get(key).set_data((x_data, y_data))
        for key in list(self.lines):
            if key not in data.keys():
                line = self.lines.pop(key)
                line.remove()

    def draw(self):
        def draw():
            try:
                self.canvas.draw()
                self.canvas.flush_events()
            except:
                pass
            self.root.after(UPDATE_INTERVAL, draw)

        self.root.after(UPDATE_INTERVAL, draw)


class Graph:
    def __init__(self, x_data, y_data=None):
        self.fig = Figure(figsize=(12, 6))
        self.ax = self.fig.add_subplot(111)
        self.is_plotting = False
        self.master = None
        self.canvas = None
        self.toolbar = None
        if y_data is not None:
            self.line, = self.ax.plot(x_data, y_data, linewidth=0.5)
        else:
            self.line, = self.ax.plot(x_data, linewidth=0.5)

    def start(self, master):
        self.is_plotting = True
        self.master = master
        self.canvas = FigureCanvasTkAgg(self.fig, master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update(self, data):
        self.line.set_ydata(data)

    def draw(self):
        try:
            self.canvas.draw()
            self.canvas.flush_events()
        except KeyboardInterrupt:
            raise
        except:
            self.is_plotting = False

    def __del__(self):
        print("Deleting graph")

    def close(self):
        self.master.destroy()
        print("Closing graph")
        del self


