import tkinter as tk
from typing import List, Dict

from .. import mvc
from ..manager import TaskInterface


class BoxedEntriesFrame(tk.Frame):
    class BoxedEntry(tk.Frame):
        def __init__(self, master):
            super().__init__(master)
            self.variable = variable = tk.IntVar(self, 1)

            self.check_button = tk.Checkbutton(self, variable=variable)
            self.check_button.pack(side='left')

            self.entry = tk.Entry(self, width=30)
            self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

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


class View(mvc.ViewOld):
    def __init__(self, master):
        super().__init__(master)

        self.create_label_header('Graph filters:')
        self.filter = BoxedEntriesFrame(self)
        self.filter.pack(fill='both', pady=5)

        self.create_group('Settings')
        self.create_group('Filters')

        self.create_grouped_button('Filters', 'Add', 'Add filter')
        self.create_grouped_button('Filters', 'Remove', 'Remove filter')
        self.create_grouped_button('Settings', 'Save', 'Save filters')
        self.create_grouped_button('Settings', 'Restore', 'Restore filters')


class Model(mvc.ModelOld):
    filter_data: List[Dict[str, any]]

    def __init__(self):
        super().__init__('filters')
        self.filter_data = []
        self.settings.update({
            'filters': self.filter_data,
        })

    def save(self):
        self.settings['filters'] = self.filter_data
        super(Model, self).save()

    def load(self):
        super(Model, self).load()
        self.filter_data.clear()
        self.filter_data.extend(self.settings['filters'])
        self.settings['filters'] = self.filter_data


class Controller(mvc.ControllerOld):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.model.bind(interface)
        self.view = View(master)
        self.view.pack(fill='both', side='left', padx=5, pady=5)

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
        self.view.winfo_toplevel().event_generate('<<UpdateFilters>>')

    def command_restore(self):
        self.model.load()
        self.update_view()
        self.view.winfo_toplevel().event_generate('<<UpdateFilters>>')

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
