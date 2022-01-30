import tkinter as tk
from tkinter import ttk
import threading

from interfacegraph import GraphBase
from program import SerialHandler, SerialThread
from typing import Dict



class InterfaceVariables:
    tk_data: Dict[str, tk.Variable] = {}
    serial_data: Dict[str, list] = {}
    graph_data: Dict[any, list] = {}
    arduino = SerialHandler()
    running = threading.Event()

    def __init__(self):
        self.thread = SerialThread(self.running, self.arduino)


def make_check_button(root, interface_variables: dict, name):
    interface_variables[name] = check_var = tk.IntVar(root, value=0)
    check_button = tk.Checkbutton(root, text=name, variable=check_var)
    check_button.pack(anchor='w')


def make_slider(root, interface_variables: dict, name):
    make_spaced_label(root, name)
    interface_variables[name] = scale_var = tk.DoubleVar(root, value=0)
    scale = tk.Scale(root, variable=scale_var, orient=tk.HORIZONTAL)
    scale.bind('<MouseWheel>', _make_scrolling_event(scale_var, -1))
    scale.pack(fill=tk.BOTH)


def make_spaced_label(root, text):
    make_spacer(root, 5)
    label = tk.Label(root, text=text, anchor='sw', padx=5, height=1)
    label.pack(fill=tk.BOTH)


def make_labeled_entry(root, name):
    make_spaced_label(root, name)
    entry = tk.Entry(root)
    entry.pack(fill=tk.BOTH)
    return entry


def make_updateable_label(root, interface_variables: dict, name):
    interface_variables[name] = label_var = tk.StringVar(root)
    label = tk.Label(root, textvariable=label_var, anchor='nw', padx=5, height=1)
    label.pack(fill=tk.BOTH)
    def update_label():
        text = label_var.get()
        size = text.count('\n') + 1
        label.config(height=size)
        root.after(500, update_label)

    root.after(500, update_label)


def make_spacer(root, size):
    spacer = tk.Frame(root, height=size)
    spacer.pack()


def make_button(root, command, name):
    button = tk.Button(root, text=name, command=command, height=2, anchor='w', padx=8)
    button.pack(fill=tk.BOTH)


def make_base_frame(root):
    frame = tk.Frame(root, width=1600)
    frame.pack(
        expand=False,
        fill=tk.BOTH,
        side=tk.LEFT
    )
    return frame


def make_graph(root):
    try:
        graph = GraphBase(root)
    except:
        graph = None
    return graph


def make_combobox(root, interface_variables: dict, selector):
    make_spaced_label(root, f'Select {selector}:')
    combobox = ttk.Combobox(root)
    combobox.pack()
    combobox.set('None')
    interface_variables[selector] = values = []

    def update_combobox():
        if 'None' in values:
            values.remove('None')
        if len(values) == 0:
            values.append('None')
        combobox['values'] = values
        if combobox.get() not in values:
            combobox.set(values[0])
        root.after(500, update_combobox)

    root.after(500, update_combobox)
    return combobox


def _make_scrolling_event(tk_var: tk.Variable, multiplier=1):
    def scrolling(event):
        value = tk_var.get()
        try:
            value = float(value) + multiplier * (event.delta / 120)
            tk_var.set(f'{value:.2f}')
        except:
            pass

    return scrolling
