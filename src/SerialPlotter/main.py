import tkinter as tk
from tkinter import ttk as ttk
from typing import Dict

from . import mvc, files
from .manager import TaskInterface
from .panels import communication, connection, recorder, filters, graph, formatter


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
        self.create_notebook_tab('Graph')
        self.create_notebook_tab('Settings')

    def create_notebook_tab(self, name: str):
        # Adds a tab to the notebook
        frame = tk.Frame(self.notebook)
        frame.configure(pady=5, padx=5)
        frame.pack(fill='both', expand=True, side='left')
        self.notebook.add(frame, text=name)
        self.notebook_tabs[name] = frame
        return frame


class ApplicationModel(mvc.Model):

    def __init__(self):
        super().__init__(None)
        self.settings.update({
            'version': '2.0',
        })

    def save(self):
        files.json_save(self.settings)

    def load(self):
        settings = files.json_load()
        self.settings.update(settings)
        self.settings.update({
            'version': '2.0',
        })

class ApplicationController(mvc.Controller):
    def __init__(self, master: tk.Tk, interface: TaskInterface):
        self.model = ApplicationModel()
        self.view = ApplicationView(master)
        self.view.pack(fill='both', expand=True)
        self.master = master
        self.interface = interface
        interface.application_settings = self.model.settings

        # Gather the frames of the notebook tabs
        tab_connection = self.view.notebook_tabs['Connection']
        tab_recorder = self.view.notebook_tabs['Recorder']
        tab_graph_display = self.view.notebook_tabs['Graph']
        tab_graph_settings = self.view.notebook_tabs['Settings']

        # Create sub controllers and link it to the notebook tabs
        self.connection_controller = connection.Controller(tab_connection, interface)
        self.communication_controller = communication.Controller(tab_connection, interface)
        self.recorder_controller = recorder.Controller(tab_recorder, interface)
        self.format_controller = formatter.Controller(tab_recorder, interface)
        self.filter_controller = filters.Controller(tab_graph_display, interface)
        self.graph_controller = graph.Controller(tab_graph_display, interface)

    def on_close(self):
        # Called when the user wants to close the application
        self.master.after(100, self.master.quit)
        self.interface.tasks_manager.stop()
        # Run the close procedure in the controllers
        self.connection_controller.on_close()
        self.communication_controller.on_close()
        self.recorder_controller.on_close()
        self.format_controller.on_close()
        self.filter_controller.on_close()
        self.graph_controller.on_close()

    def update_model(self):
        pass

    def update_view(self):
        pass

    def todo(self):
        pass


def __main__():
    # Root of tkinter
    root = tk.Tk()

    # Creating interface between threads
    interface = TaskInterface()

    # Creating the application
    controller = ApplicationController(root, interface)
    interface.tasks_manager.start()

    # Protocol when the user want to close the window
    root.protocol('WM_DELETE_WINDOW', controller.on_close)
    root.mainloop()

    # Try to wait for threads to finish else force exit
    interface.tasks_manager.exit(3)


if __name__ == '__main__':
    __main__()
