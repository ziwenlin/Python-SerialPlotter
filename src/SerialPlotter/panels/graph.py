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
        self.figure.subplots_adjust(0.05, 0.08, 0.97, 0.95)

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
        index = len(self.lines)
        line = Line2D([], [], linewidth=1, color=f'C{index}')
        self.plot.add_line(line)
        self.lines.append(line)

    def remove_line(self):
        line = self.lines.pop()
        line.set_label(s=None)
        line.remove()

    def draw(self):
        if self.winfo_viewable() == 0:
            return
        self.canvas.flush_events()
        self.canvas.draw_idle()


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)
        self.config(width=2000)
        self.graph = GraphFrame(self)
        self.graph.pack(fill='both', expand=True)
        self.graph.plot.set_xlim(-10, 510)
        self.graph.plot.set_ylim(-4, 54)


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

        self.view.after(1000, self.update_loop)
        self.view.after(1000, self.update_graph_legend)
        self.queue_data = interface.serial_interface.create_queue('data')
        self.view.winfo_toplevel().bind('<<UpdateFilters>>', lambda e: self.update_graph_legend(), add='+')

    def update_loop(self):
        queue_state = not self.queue_data.empty()
        while not self.queue_data.empty():
            values = self.queue_data.get()
            self.update_model_data(values)
        # This reduces cpu usage
        if queue_state is True:
            self.update_lines_data()
            self.view.graph.draw()
        self.view.after(10, self.update_loop)

    def update_model_data(self, values):
        model_data = self.model.data

        # Remove or create list to match the amount of data lines
        while len(model_data) < len(values):
            model_data.append([])
        while len(model_data) > len(values):
            model_data.pop()

        # Update the graph labels and visibility
        for list_values, value in zip(model_data, values):
            if len(list_values) > 500:
                del list_values[:50]  # Clean up
            list_values.append(value)

    def update_lines_data(self):
        graph = self.view.graph
        model_data = self.model.data

        # Pair lines and model data together
        for line, y_values in zip(graph.lines, model_data):
            x_axis = [i for i in range(len(y_values))]
            line.set_data(x_axis, y_values)

    def update_graph_legend(self):
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
            if state == 1:
                line.set_label(s=name)
            else:
                line.set_label(s=None)
            line.set_visible(state == 1)
        # Update the legend of the plot
        active_lines = [line for line in graph.lines if line.get_visible()]
        graph.plot.legend(handles=active_lines, loc='upper left')
        graph.draw()

    def on_close(self):
        pass

    def update_model(self):
        pass

    def update_view(self):
        pass
