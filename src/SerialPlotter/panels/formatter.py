import tkinter

from .. import mvc
from ..manager import TaskInterface


class Model(mvc.Model):
    def __init__(self):
        super().__init__('format')
        self.settings.update({
            'decimal': 'Comma',
            'delimiter': 'Semicolon',
        })


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        self.create_label_header('Select delimiter:')
        delimiters = self.create_combobox('delimiter', 'Comma')
        delimiters['values'] = ['Comma', 'Dot', 'Semicolon', 'Colon', 'Tab', ]

        self.create_label_header('Select decimal:')
        decimals = self.create_combobox('decimal', 'Dot')
        decimals['values'] = ['Dot', 'Comma', ]


class Controller(mvc.Controller):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.model.bind(interface)
        self.view = View(master)
        self.view.pack(fill='both', side='left', padx=5, pady=5)
        self.view.winfo_toplevel().bind('<<UpdateRecorder>>', lambda e: self.command_settings(), '+')

        self.model.load()
        self.update_view()
        self.queue_command = interface.storage_interface.queue_command
        self.queue_status = interface.storage_interface.queue_status

    def command_settings(self):
        delimiter = self.view.combo_boxes['delimiter'].get()
        self.queue_command.put('delimiter ' + delimiter.lower())

        decimal = self.view.combo_boxes['decimal'].get()
        self.queue_command.put('decimal ' + decimal.lower())

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        settings = self.model.settings
        settings['decimal'] = self.view.combo_boxes['decimal'].get()
        settings['delimiter'] = self.view.combo_boxes['delimiter'].get()

    def update_view(self):
        settings = self.model.settings
        self.view.combo_boxes['decimal'].delete(0, tkinter.END)
        self.view.combo_boxes['decimal'].insert(0, settings['decimal'])
        self.view.combo_boxes['delimiter'].delete(0, tkinter.END)
        self.view.combo_boxes['delimiter'].insert(0, settings['delimiter'])
