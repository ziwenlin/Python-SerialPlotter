import abc
import tkinter as tk
from tkinter import ttk as ttk
from typing import Dict

from . import files
from .manager import TaskInterface


class ViewOld(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.frames: Dict[str, tk.Frame] = {}
        self.text_field: Dict[str, tk.Text] = {}
        self.spin_boxes: Dict[str, tk.StringVar] = {}
        self.combo_boxes: Dict[str, ttk.Combobox] = {}
        self.check_buttons: Dict[str, tk.IntVar] = {}
        self.radio_buttons: Dict[str, tk.IntVar] = {}
        self.scales: Dict[str, tk.DoubleVar] = {}
        self.labels: Dict[str, tk.Label] = {}
        self.buttons: Dict[str, tk.Button] = {}
        self.entries: Dict[str, tk.Entry] = {}

    def update_label(self, name: str, text: str):
        """
        Updates the text inside the desired label.

        :param name: Name of the label
        :param text: Desired text which will be displayed
        """
        label = self.labels.get(name)
        wrap = label.winfo_width() - 20
        font = tk.font.nametofont(label['font'])
        text_height = sum([font.measure(t) // wrap for t in text.split('\n')])
        label_height = text.count('\n') + text_height + 1
        label.config(height=label_height, text=text, wraplength=wrap)

    def bind_button(self, name: str, command: ()):
        """
        Binds the command to the desired button.

        :param name: Name of the button
        :param command: Desired function
        """
        button = self.buttons.get(name)
        button.configure(command=command)

    def create_button(self, name: str, text: str):
        """
        Creates a button with the desired text.

        :param name: Name of the button
        :param text: Text which will be displayed on the button
        """
        button = tk.Button(self, text=text)
        button.configure(anchor='w', padx=8, pady=6)
        button.pack(fill='both')
        self.buttons[name] = button
        return button

    def create_group(self, group_name: str):
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=10)
        self.frames[group_name] = frame
        return frame

    def create_grouped_button(self, group: str, name: str, text: str):
        frame = self.frames[group]
        index = len(frame.winfo_children())
        frame.grid_columnconfigure(index, weight=1, uniform=group)

        button = tk.Button(frame, text=text)
        button.configure(anchor='center', padx=8, pady=4)
        button.grid(row=0, column=index, padx=1, sticky='we')
        self.buttons[name] = button
        return button

    def create_label(self, name, text):
        """
        Creates a label with the desired text.

        :param name: Name of the label
        :param text: Desired text which will be displayed
        """
        label = tk.Label(self, text=text)
        label.configure(anchor='nw', height=1, width=3, justify='left')
        label.pack(fill='both', pady=2, padx=10)
        self.labels[name] = label
        return label

    def create_label_header(self, text):
        """
        Creates a label with the desired text.

        :param text: Desired text which will be displayed
        """
        label = tk.Label(self, text=text)
        label.configure(anchor='nw', padx=5, height=1)
        label.pack(fill='both', pady=(15, 0))
        return label

    def create_labeled_entry(self, name: str, text: str):
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=2, padx=10)
        frame.grid_columnconfigure(1, weight=2, uniform='LE')
        frame.grid_columnconfigure(0, weight=1, uniform='LE')

        self.entries[name] = entry = tk.Entry(frame)
        entry.grid(row=0, column=1, sticky='we')
        label = tk.Label(frame, text=text)
        label.grid(row=0, column=0, sticky='w', padx=(0, 10))
        return frame, label, entry

    def create_check_button(self, name: str, text: str):
        """
        Creates a checkbutton with the desired text

        :param name: Name of the check button
        :param text: Text which will be displayed on the button
        """
        self.check_buttons[name] = variable = tk.IntVar()
        check_button = tk.Checkbutton(self, text=text, variable=variable)
        check_button.pack(anchor='w', padx=(5, 5))
        return check_button, variable

    def create_entry(self, name: str):
        self.entries[name] = entry = tk.Entry(self)
        entry.pack(fill='both', pady=(5, 10), padx=5)
        return entry

    def create_entry_with_button(self, name: str, text: str):
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=(5, 10), padx=5)
        frame.grid_columnconfigure(1, weight=5, uniform='EB')
        frame.grid_columnconfigure(0, weight=1, uniform='EB')

        self.entries[name] = entry = tk.Entry(frame)
        entry.grid(row=0, column=1, sticky='we')

        self.buttons[name] = button = tk.Button(frame, text=text)
        button.configure(anchor='center', padx=8)
        button.grid(row=0, column=0, sticky='we', padx=(0, 5))

        return frame, entry, button

    def create_combobox(self, name, default_value, values=None):
        if values is None:
            values = []

        self.combo_boxes[name] = combobox = ttk.Combobox(self, values=values)
        combobox.pack(fill='both', padx=(5, 0), pady=(5, 10))
        combobox.set(default_value)
        return combobox

    def create_text_field(self, name):
        frame = tk.Frame(self)
        frame.pack(fill='both', expand=True, pady=(5, 20), padx=5)

        self.text_field[name] = text = tk.Text(frame)
        text.configure(padx=5, pady=5, height=3, width=5)
        text.pack(fill='both', expand=True, side='left')

        scroll = tk.Scrollbar(frame)
        scroll.pack(fill='both', side='right')

        text.configure(yscrollcommand=scroll.set)
        scroll.configure(command=text.yview)

        return frame, text, scroll

    def create_radio_buttons(self, name, values):
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=5)

        radio_buttons = []
        self.radio_buttons[name] = variable = tk.IntVar(value=0)

        for index, text in enumerate(values):
            radio_button = tk.Radiobutton(frame, text=text, variable=variable, value=index)
            radio_button.pack(anchor='w', side='left')
            radio_buttons.append(radio_button)

        return frame, radio_buttons, variable

    def create_ranged_slider(self, name, text, limits=(-10, 10, 0.1)):
        a, b, c = limits
        ratio_a = abs(a) / (b - a) * 100
        ratio_b = abs(b) / (b - a) * 100

        frame = tk.Frame(self)
        frame.pack(fill='both', padx=5, pady=5)

        label = tk.Label(frame, text=text)
        label.pack(side='left', fill='both', anchor='e')

        self.scales[name + 'Min'] = variable = tk.DoubleVar(frame)
        scale = tk.Scale(frame, variable=variable, orient='horizontal', length=ratio_a, from_=a, to=0)
        scale.pack(side='left', fill='both', expand=True)

        self.scales[name + 'Max'] = variable = tk.DoubleVar(frame)
        scale = tk.Scale(frame, variable=variable, orient='horizontal', length=ratio_b, from_=1, to=b)
        scale.pack(side='left', fill='both', expand=True)

    def create_spinbox(self, name, text, limits=(-10, 10, 0.1)):
        a, b, c = limits
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=5)

        label = tk.Label(frame, text=text)
        label.pack(side='left', fill='both', anchor='e')

        self.spin_boxes[name] = variable = tk.StringVar(frame, value='0')
        spinbox = tk.Spinbox(frame, textvariable=variable, from_=a, to=b, increment=c)
        spinbox.bind('<MouseWheel>', _scrolling_event(variable, 5 * c))
        spinbox.pack(side='right', fill='both', anchor='w')


def _scrolling_event(tk_var: tk.StringVar, multiplier: float = 1):
    def scrolling(event):
        value = tk_var.get()
        try:
            value = float(value) + multiplier * (event.delta / 120)
            tk_var.set(f'{value:.2f}')
        except ValueError:
            tk_var.set('0')

    return scrolling


class ModelOld:
    settings: Dict[str, any]

    def __init__(self, name):
        self.__name: str = name
        self.settings = {}

    def save(self):
        if self.__name is None:
            return
        if len(self.settings) == 0:
            return
        settings = files.json_load()
        settings[self.__name] = self.settings
        files.json_save(settings)

    def load(self):
        settings = files.json_load()
        if self.__name in settings:
            setting = settings[self.__name]
            self.settings.update(setting)

    def bind(self, interface: TaskInterface):
        if self.__name is None:
            self.settings = interface.application_settings
            return
        if self.__name not in interface.application_settings:
            interface.application_settings[self.__name] = self.settings
            return
        interface.application_settings[self.__name].update(self.settings)
        self.settings = interface.application_settings[self.__name]


class ControllerOld:
    @abc.abstractmethod
    def on_close(self):
        pass

    @abc.abstractmethod
    def update_model(self):
        pass

    @abc.abstractmethod
    def update_view(self):
        pass
