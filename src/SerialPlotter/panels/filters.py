import tkinter as tk
from typing import List, Dict

from .. import mvc
from ..filehandler import json_load, json_save
from ..thread import ThreadInterface


class BoxedEntriesFrame(tk.Frame):
    class BoxedEntry(tk.Frame):
        def __init__(self, master):
            super().__init__(master)
            self.variable = variable = tk.IntVar(self)

            self.check_button = tk.Checkbutton(self, variable=variable)
            self.check_button.pack(side='left')

            self.entry = tk.Entry(self)
            self.entry.pack(side='left', fill='x')

        def get_elements(self):
            return self.variable, self.check_button, self.entry

        def get_values(self):
            return self.variable.get(), self.entry.get()

        def set_values(self, state: int, text: str):
            self.variable.set(state)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)

    def __init__(self, master):
        super().__init__(master)
        self.entries: List[BoxedEntriesFrame.BoxedEntry] = []
        self.create_entry()

    def remove_entry(self):
        if len(self.entries) <= 1:
            return
        frame = self.entries.pop()
        for child in frame.winfo_children():
            child.destroy()
        frame.destroy()

    def create_entry(self):
        frame = BoxedEntriesFrame.BoxedEntry(self)
        frame.pack(fill='both', expand=True, side='top', anchor='n')

        self.entries.append(frame)
        return frame


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        self.create_label_header('Graph filters:')

        self.filter = BoxedEntriesFrame(self)
        self.filter.pack(fill='both', pady=5)

        self.create_button('Restore', 'Restore filter').pack(side='bottom')
        self.create_button('Save', 'Save filter').pack(side='bottom')
        self.create_button('Remove', 'Remove filter').pack(side='bottom')
        self.create_button('Add', 'Add filter').pack(side='bottom')


class Model(mvc.Model):
    filter_data: List[Dict[str, any]]

    def __init__(self):
        self.filter_data = []

    def save(self):
        settings = json_load()
        settings['filters'] = self.filter_data
        json_save(settings)

    def load(self):
        settings = json_load()
        if 'filters' in settings:
            self.filter_data = settings['filters']


class Controller(mvc.Controller):
    def __init__(self, master, interface: ThreadInterface):
        self.interface = interface
        self.model = Model()
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)

        self.view.bind_button('Add', self.command_add)
        self.view.bind_button('Remove', self.command_remove)
        self.view.bind_button('Save', self.command_save)
        self.view.bind_button('Restore', self.command_restore)

        self.model.load()
        self.update_view()

    def command_remove(self):
        self.view.filter.remove_entry()

    def command_add(self):
        self.view.filter.create_entry()

    def command_save(self):
        self.update_model()
        self.model.save()

    def command_restore(self):
        self.model.load()
        self.update_view()

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        frame = self.view.filter
        self.model.filter_data.clear()
        for entry in frame.entries:
            state, text = entry.get_values()
            self.model.filter_data.append({
                'state': state,
                'name': text,
            })

    def update_view(self):
        frame = self.view.filter
        amount = len(self.model.filter_data) - len(frame.entries)
        for _ in range(-amount):
            frame.remove_entry()
        for _ in range(amount):
            frame.create_entry()
        for entry, values in zip(frame.entries, self.model.filter_data):
            entry.set_values(values['state'], values['name'])
