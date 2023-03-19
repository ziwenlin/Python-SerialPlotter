import tkinter as tk
from typing import Dict

from .. import mvc
from ..files import json_load, json_save
from ..manager import TaskInterface


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
            'Disable', 'Show input', 'Show messages', 'Show values'])
        self.create_text_field('In')


class Model(mvc.Model):
    def __init__(self):
        super().__init__('communication')
        self.settings.update({
            'command': '',
            'show': 0,
            'keep': 0,
        })


class Controller(mvc.Controller):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)
        self.view.bind_button('Out', self.command_send)

        self.model.load()
        self.update_view()
        self.queue_in = interface.serial_interface.create_queue('in')
        self.queue_out = interface.serial_interface.create_queue('out')
        self.queue_data = interface.serial_interface.create_queue('data')
        self.queue_messages = interface.serial_interface.create_queue('text')
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
        state = self.view.radio_buttons['Show'].get()
        while not self.queue_in.empty():
            text = str(self.queue_in.get())
            if state != 1: continue
            self.view.text_field['In'].insert('1.0', text)
        while not self.queue_data.empty():
            text = str(self.queue_data.get()) + '\n'
            if state != 3: continue
            self.view.text_field['In'].insert('1.0', text)
        while not self.queue_messages.empty():
            text = str(self.queue_messages.get())
            if state != 2: continue
            self.view.text_field['In'].insert('1.0', text)
        self.view.after(200, self.display_incoming_text)

    def command_send(self):
        entry = self.view.entries['Out']
        state = self.view.radio_buttons['Remember'].get()
        data = entry.get()
        if state == 0:
            entry.delete(0, tk.END)
        self.view.text_field['In'].insert('1.0', 'Command send: ' + data + '\n')
        self.queue_out.put(data)
