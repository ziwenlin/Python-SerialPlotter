import abc
import tkinter as tk
from tkinter import ttk as ttk
from typing import Dict

from . import files
from .manager import TaskInterface


class View(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text_field: Dict[str, tk.Text] = {}
        self.spin_boxes: Dict[str, tk.StringVar] = {}
        self.combo_boxes: Dict[str, ttk.Combobox] = {}
        self.check_buttons: Dict[str, tk.IntVar] = {}
        self.radio_buttons: Dict[str, tk.IntVar] = {}
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
        wrap = label.winfo_width()
        font = tk.font.nametofont(label['font'])
        text_height = font.measure(text) // wrap
        label_height = text.count('\n') + text_height + 1
        label.config(height=label_height, text=text, wraplength=wrap - 10)

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
        button.configure(height=2, anchor='w', padx=8)
        button.pack(fill='both')
        self.buttons[name] = button
        return button

    def create_label(self, name, text):
        """
        Creates a label with the desired text.

        :param name: Name of the label
        :param text: Desired text which will be displayed
        """
        label = tk.Label(self, text=text)
        label.configure(anchor='nw', padx=10, height=1, width=3, justify='left')
        label.pack(fill='both', pady=2)
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

    def create_check_button(self, name: str, text: str):
        """
        Creates a checkbutton with the desired text

        :param name: Name of the check button
        :param text: Text which will be displayed on the button
        """
        self.check_buttons[name] = variable = tk.IntVar()
        check_button = tk.Checkbutton(self, text=text, variable=variable)
        check_button.pack(anchor='w')
        return check_button, variable

    def create_entry(self, name: str):
        self.entries[name] = entry = tk.Entry(self)
        entry.pack(fill='both', pady=(5, 10), padx=5)
        return entry

    def create_entry_with_button(self, name: str, text: str):
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=(5, 10), padx=5)

        self.entries[name] = entry = tk.Entry(frame)
        entry.pack(fill='both', side='left', expand=True)

        self.buttons[name] = button = tk.Button(frame, text=text)
        button.configure(anchor='w', padx=8)
        button.pack(fill='both', side='right', padx=(5, 0))

        return frame, entry, button

    def create_combobox(self, name, default_value, values=None):
        if values is None:
            values = []

        self.combo_boxes[name] = combobox = ttk.Combobox(self, values=values)
        combobox.pack(fill='both', padx=5, pady=(5, 20))
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


class Model:
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
        interface.application_settings[self.__name] = self.settings


class Controller:
    @abc.abstractmethod
    def on_close(self):
        pass

    @abc.abstractmethod
    def update_model(self):
        pass

    @abc.abstractmethod
    def update_view(self):
        pass
