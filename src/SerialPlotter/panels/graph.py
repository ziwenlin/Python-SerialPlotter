import tkinter as tk
from typing import List, Dict

from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from .. import mvc
from ..manager import TaskInterface


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

    def create_line(self):
        line = Line2D([], [], linewidth=1)
        self.plot.add_line(line)
        self.lines.append(line)

    def remove_line(self):
        line = self.lines.pop(0)
        line.remove()

    def draw(self):
        self.canvas.draw()
        self.canvas.flush_events()


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)
        self.config(width=2000)
        self.graph = GraphFrame(self)
        self.graph.pack(fill='both', expand=True)


class Model(mvc.Model):
    data: List[List[float]]
    filters: List[Dict[str, any]]

    def __init__(self):
        super().__init__(None)
        self.filters = []
        self.data = []

    def bind(self, interface: TaskInterface):
        super().bind(interface)
        self.filters = self.settings['filters']['filters']


class Controller(mvc.Controller):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.model.bind(interface)
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)

        self.view.winfo_toplevel().bind('<<UpdateFilters>>', self.update_graph_legend, add='+')

    def update_graph_legend(self, event=None):
        """
        Updates the legend of the graph.
        """
        filter_list = self.model.filters
        graph = self.view.graph

        # Remove or create lines to match the amount of filters
        num_filters = len(filter_list)
        while len(graph.lines) < num_filters:
            graph.create_line()
        while len(graph.lines) > num_filters:
            graph.remove_line()

        # Update the graph labels and visibility
        for filter, line in zip(filter_list, graph.lines):
            state = filter['state']
            name = filter['name']
            line.set_visible(state == 1)
            line.set_label(name)
        # Update the legend of the plot
        graph.plot.legend(handles=graph.lines)
        graph.draw()

    def on_close(self):
        pass

    def update_model(self):
        pass

    def update_view(self):
        pass
