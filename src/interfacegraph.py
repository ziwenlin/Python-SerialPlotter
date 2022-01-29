import tkinter as tk

import matplotlib.axes
import numpy.random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
from typing import List, Dict


class GraphBase:

    def __init__(self, root: tk.BaseWidget):
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, root)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.root = root
        self.draw()
        self.ax: Axes = self.figure.add_subplot()
        self.lines: Dict[str, Line2D] = {}

    def update(self, data: Dict[str, list]):
        for key, y_data in data.items():
            length = len(y_data)
            x_data = [x for x in range(length)]
            if key not in self.lines:
                lines = self.ax.plot(x_data, y_data)
                self.lines.update({key: lines[0]})
            self.lines.get(key).set_data((x_data, y_data))

    def draw(self):
        def draw():
            self.canvas.draw()
            self.canvas.flush_events()
            self.root.after(20, draw)

        self.root.after(20, draw)


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


def main0():
    root = tk.Tk()
    data_x = [_ for _ in range(100)]
    data_y = [_ for _ in range(100)]
    graph = Graph(data_x)
    graph.start(root)

    def update():
        a = data_y[-1]
        for x in data_x:
            y = data_y[x]
            data_y[x - 1] = y
        data_y[-2] = a
        graph.update(data_y)
        graph.draw()
        root.after(10, update)

    root.after(100, update)
    root.mainloop()


def main():
    root = tk.Tk()
    graph = GraphBase(root)

    def update():
        increase[0] += 1
        data = {}
        data.update({'Test': numpy.random.random(increase[0])})
        if increase[0] > 15:
            data.update({'Test1': numpy.random.random(increase[0] - 3)})
        if increase[0] > 20:
            data.update({'Test2': numpy.random.random(increase[0] + 4)})

        graph.ax.set_ylim(0, 1)
        graph.ax.set_xlim(0, increase[0])
        graph.update(data)

    increase = [5]
    button = tk.Button(root, command=update)
    button.pack()
    root.mainloop()


if __name__ == '__main__':
    import tkinter as tk

    main()
