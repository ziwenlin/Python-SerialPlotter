import tkinter as tk
from queue import Queue
from typing import Dict

from .. import mvc
from ..filehandler import json_load, json_save, csv_save_append, csv_save_create
from ..interfacebuilder import make_thread
from ..threadbuilder import build_thread_csv


class View(mvc.View):
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


class Model(mvc.Model):
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


class Controller(mvc.Controller):
    def __init__(self, master, interface):
        self.interface = interface
        self.model = Model()
        self.view = View(master)
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
