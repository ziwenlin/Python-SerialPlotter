import tkinter as tk
from typing import Dict

from .. import mvc
from ..files import json_load, json_save
from ..manager import ThreadInterface


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        # Header label send command
        # Entry for send command
        # Button which sends the command
        self.create_label_header('Send command to device:')
        self.create_radio_buttons('Remember', [
            'Remove after send', 'Keep after send',
            'Keep and send when connecting'])
        self.create_entry_with_button('Out', 'Send')

        # Header label incoming data
        self.create_label_header('Incoming data:')
        self.create_radio_buttons('Show', [
            'Disable', 'Show all', 'Show messages', 'Show values'])
        self.create_text_field('In')


class Model(mvc.Model):
    settings: Dict[str, any]

    def __init__(self):
        self.settings = {
            'command': '',
            'show': 0,
            'keep': 0,
        }

    def save(self):
        settings = json_load()
        settings['iostream'] = self.settings
        json_save(settings)

    def load(self):
        settings = json_load()
        if 'iostream' in settings:
            self.settings = settings['iostream']


class Controller(mvc.Controller):
    def __init__(self, master, interface: ThreadInterface):
        self.interface = interface
        self.model = Model()
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)
        self.view.bind_button('Out', self.command_send)

        self.model.load()
        self.update_view()
        self.view.after(1000, self.display_incoming_text)

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        settings = self.model.settings
        settings['command'] = self.view.entries['Out'].get()
        settings['show'] = self.view.radio_buttons['Show'].get()
        settings['keep'] = self.view.radio_buttons['Remember'].get()

    def update_view(self):
        settings = self.model.settings
        self.view.entries['Out'].delete(0, tk.END)
        self.view.entries['Out'].insert(0, settings['command'])
        self.view.radio_buttons['Show'].set(settings['show'])
        self.view.radio_buttons['Remember'].set(settings['keep'])

    def display_incoming_text(self):
        queue = self.interface.serial_controller.queue_in
        state = self.view.radio_buttons['Show'].get()
        while not queue.empty():
            # Wrong queue, need to change it in the future
            text = str(queue.get()) + '\n'
            if state == 0: continue
            self.view.text_field['In'].insert('1.0', text)
        self.view.after(500, self.display_incoming_text)

    def command_send(self):
        entry = self.view.entries['Out']
        state = self.view.radio_buttons['Remember'].get()
        data = entry.get()
        if state == 0:
            entry.delete(0, tk.END)
        self.view.text_field['In'].insert('1.0', 'Command send: ' + data + '\n')
        self.interface.serial_controller.queue_out.put(data)
