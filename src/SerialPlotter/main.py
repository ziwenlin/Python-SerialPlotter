import tkinter as tk
from tkinter import ttk as ttk
from typing import Dict

from . import mvc
from .interfacebuilder import make_base_frame, InterfaceVariables, make_graph, make_thread
from .panels import connection, device, recorder, graph_filter
from .threadbuilder import build_thread_graph


class ApplicationView(mvc.View):
    def __init__(self, master):
        super().__init__(master)
        self.notebook_tabs: Dict[str, tk.Frame] = {}

        # Create a notebook as main menu
        self.notebook = notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, fill='both', expand=True, anchor='w')

        # Create the tab frames
        self.create_notebook_tab('Connection')
        self.create_notebook_tab('Recorder')
        self.create_notebook_tab('Graph display')
        self.create_notebook_tab('Graph settings')

    def create_notebook_tab(self, name: str):
        frame = tk.Frame(self.notebook)
        frame.configure(pady=5, padx=5)
        frame.pack(fill='both', expand=True, side='left')
        self.notebook.add(frame, text=name)
        self.notebook_tabs[name] = frame
        return frame


class ApplicationController(mvc.Controller):
    def __init__(self, master: tk.Tk, interface):
        self.view = ApplicationView(master)
        self.view.pack(fill='both', expand=True)
        self.master = master
        self.interface = interface

        # Gather the frames of the notebook tabs
        tab_connection = self.view.notebook_tabs['Connection']
        tab_recorder = self.view.notebook_tabs['Recorder']
        tab_graph_display = self.view.notebook_tabs['Graph display']
        tab_graph_settings = self.view.notebook_tabs['Graph settings']

        # Create sub controllers and link it to the notebook tabs
        self.device_controller = device.Controller(tab_connection, interface)
        self.connection_controller = connection.Controller(tab_connection, interface)
        self.recorder_controller = recorder.Controller(tab_recorder, interface)
        self.graph_filter_controller = graph_filter.Controller(tab_graph_display, interface)

        # Fill the tabs with the content
        panel_graph_view(tab_graph_display, interface)

    def on_close(self):
        self.device_controller.on_close()
        self.connection_controller.on_close()
        self.recorder_controller.on_close()
        self.graph_filter_controller.on_close()
        self.interface.import_settings()
        self.master.after(100, self.master.destroy)

    def update_model(self):
        pass

    def update_view(self):
        pass

    def todo(self):
        pass


def panel_graph_view(base, interface: InterfaceVariables):
    frame = make_base_frame(base)
    frame.config(width=2000)
    graph = make_graph(frame)

    interface.tk_data['graph'] = button_list = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13'
    ]
    for name in button_list:
        interface.tk_vars[name] = tk.IntVar(frame, value=0)
    interface.graph_data['state'] = {}

    make_thread(build_thread_graph(graph, interface), interface, 'Serial graph')


def __main__():
    root = tk.Tk()
    # To be done: This should be model
    interface = InterfaceVariables()

    controller = ApplicationController(root, interface)
    root.protocol('WM_DELETE_WINDOW', controller.on_close)

    # To be done: Change interface to controller
    interface.import_settings()
    interface.start_threads()
    root.mainloop()
    interface.stop_threads()
    interface.export_settings()


if __name__ == '__main__':
    __main__()
