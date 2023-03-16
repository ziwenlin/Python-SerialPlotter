import tkinter as tk
from queue import Queue
from tkinter import ttk as ttk
from typing import Dict

from . import mvc
from .filehandler import csv_save_append, csv_save_create, json_load, json_save
from .interfacebuilder import make_base_frame, InterfaceVariables, make_graph, make_thread
from .panels import device
from .panels import graph_filter
from .threadbuilder import build_thread_graph, build_thread_csv


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
        self.connection_controller = ConnectionPanelController(tab_connection, interface)
        self.recorder_controller = RecorderPanelController(tab_recorder, interface)
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


class ConnectionPanelView(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        # Header label send command
        # Entry for send command
        # Button which sends the command
        self.create_label_header('Send command to device:')
        self.create_entry_with_button('Out', 'Send')

        # Header label connection settings
        self.create_label_header('Connection data settings:')

        # Header label incoming data
        self.create_label_header('Incoming data:')
        self.create_radio_buttons('Show', [
            'Disable', 'Show all', 'Show messages', 'Show values'])
        self.create_text_field('In')


class ConnectionPanelController(mvc.Controller):
    def __init__(self, master, interface):
        self.interface = interface
        self.view = ConnectionPanelView(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)
        self.view.bind_button('Out', self.send_command)

    def on_close(self):
        pass

    def update_model(self):
        pass

    def update_view(self):
        pass

    def send_command(self):
        entry = self.view.entries['Out']
        data = entry.get()
        entry.delete(0, tk.END)
        self.interface.arduino.queue_out.put(data)


class RecorderPanelView(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        # Header label file name
        self.create_label_header('Save file name:')

        # Entry for file name
        self.create_entry_with_button('Save', 'Save')

        # Header label recorder controls
        self.create_label_header('Recorder controls:')

        # Buttons with the display labels
        self.create_button('Start', 'Start')
        self.create_button('Pause', 'Pause')

        # Header label recorder status
        self.create_label_header('Recorder status:')

        # Label which will list the recorder status
        # Controller logic will update this text
        self.create_label('Status', 'Standby')

        # Header label recorder settings
        self.create_label_header('Recorder settings:')

        # Check buttons options
        self.create_check_button('Auto save', 'Automatically save incoming data')
        self.create_check_button('File append', 'Append recorder save file data when saving manually')
        self.create_check_button('File overwrite', 'Overwrite recorder save file data when saving manually')


class RecorderPanelModel(mvc.Model):
    recorder_settings: Dict[str, any]

    def __init__(self):
        self.recorder_settings = {
            'file_name': '',
            'auto_save': 0,
            'file_append': 0,
            'file_overwrite': 0,
        }

    def save(self):
        settings = json_load()
        settings['recorder'] = self.recorder_settings
        json_save(settings)

    def load(self):
        settings = json_load()
        if 'recorder' in settings:
            self.recorder_settings = settings['recorder']


class RecorderPanelController(mvc.Controller):
    def __init__(self, master, interface):
        self.interface = interface
        self.model = RecorderPanelModel()
        self.view = RecorderPanelView(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)

        self.view.bind_button('Save', self.save_command)
        self.view.bind_button('Start', self.start_command)
        self.view.bind_button('Pause', self.pause_command)

        self.model.load()
        self.update_view()

        # IDK what these would do, but it should not be in view
        self.trigger = trigger = {'start': False, 'name': self.view.entries['Save'].get()}
        interface.tk_vars['Auto save'] = self.view.check_buttons['Auto save']
        interface.graph_data['record csv'] = []
        interface.graph_data['auto csv'] = Queue()
        make_thread(build_thread_csv(trigger, interface), interface, 'Csv manager')

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        settings = self.model.recorder_settings
        settings['file_name'] = self.view.entries['Save'].get()
        settings['auto_save'] = self.view.check_buttons['Auto save'].get()
        settings['file_append'] = self.view.check_buttons['File append'].get()
        settings['file_overwrite'] = self.view.check_buttons['File overwrite'].get()

    def update_view(self):
        settings = self.model.recorder_settings
        self.view.entries['Save'].delete(0, tk.END)
        self.view.entries['Save'].insert(0, settings['file_name'])
        self.view.check_buttons['Auto save'].set(settings['auto_save'])
        self.view.check_buttons['File append'].set(settings['file_append'])
        self.view.check_buttons['File overwrite'].set(settings['file_overwrite'])

    def save_command(self):
        record_data = self.interface.graph_data['record csv']
        auto_save_var = self.view.check_buttons['Auto save']
        file_append_var = self.view.check_buttons['File append']
        file_overwrite_var = self.view.check_buttons['File overwrite']
        name = self.view.entries['Save'].get()
        # name = trigger['name']
        if auto_save_var.get() == 1:
            return
        elif file_append_var.get() == 1:
            success = csv_save_append(name, record_data)
        elif file_overwrite_var.get() == 1:
            success = csv_save_create(name, record_data)
        else:
            success = csv_save_create(name, record_data)
        if auto_save_var.get() == 0:
            record_data.clear()
        if success is True:
            success = f'Saved data to {name}.csv'
        elif success is False:
            success = f'Could not save data to {name}.csv'
        else:  # Fatal error
            success = f'Something went wrong with {name}.csv'
        self.view.update_label('Status', success)

    def start_command(self):
        self.trigger['start'] = True
        self.trigger['name'] = self.view.entries['Save'].get()
        self.view.update_label('Status', 'Started recording')

    def pause_command(self):
        self.trigger['start'] = False
        self.view.update_label('Status', 'Paused recording')


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
