import tkinter as tk
from tkinter import ttk
import threading

from filehandler import json_load, json_save
from interfacegraph import GraphBase
from program import SerialHandler, SerialThread
from typing import Dict, List

UPDATE_INTERVAL = 500


class InterfaceVariables:
    tk_vars: Dict[str, tk.Variable] = {}
    tk_data: Dict[str, list] = {}
    graph_data: Dict[str, any] = {}
    settings = json_load()
    arduino = SerialHandler()
    running = threading.Event()

    def __init__(self):
        thread_serial = SerialThread(self.running, self.arduino)
        self.threads: List[threading.Thread] = [thread_serial]

    def __del__(self):
        self.export_settings()

    def import_settings(self):
        settings = self.settings
        for key, value in settings.get('tk_vars').items():
            self.tk_vars[key].set(value)
        for key, data in settings.get('tk_data').items():
            self.tk_data[key] = data
        for key, data in settings.get('graph_data').items():
            self.graph_data[key] = data

    def export_settings(self):
        version = '1.0'
        tk_vars = {key: value.get() for key, value in self.tk_vars.items()}
        tk_data = {'graph': self.tk_data['graph']}
        gr_data = {'state': self.graph_data['state']}
        json_save({'version': version,
                   'tk_vars': tk_vars,
                   'tk_data': tk_data,
                   'graph_data': gr_data})

    def start_threads(self):
        self.running.is_set()
        for thread in self.threads:
            thread.start()

    def stop_threads(self):
        self.running.clear()
        tries = 1
        # print('Active threads now:', threading.active_count())
        while threading.active_count() > 1:
            for thread in self.threads:
                thread.join(2)
                if tries > 2 and thread.is_alive():
                    print('Stuborn thread:', thread.name)
            if tries > 3:
                print('Force close python')
                break
            else:
                tries += 1


def make_thread(target, interface: InterfaceVariables, name):
    thread = threading.Thread(target=target, daemon=True, name=name)
    interface.threads.append(thread)


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


def make_updatable_label(root: tk.Widget, interface_variables: dict, name):
    interface_variables[name] = label_var = tk.StringVar(root)
    label = tk.Label(root, textvariable=label_var, anchor='nw', padx=5, height=1)
    label.pack(fill=tk.BOTH)

    def update_label():
        text = label_var.get()
        size = text.count('\n') + 1
        label.config(height=size)
        root.after(UPDATE_INTERVAL, update_label)

    root.after(UPDATE_INTERVAL, update_label)


def make_spacer(root, size):
    spacer = tk.Frame(root, height=size)
    spacer.pack(fill=tk.BOTH)


def make_button(root, command, name):
    button = tk.Button(root, text=name, command=command, height=2, anchor='w', padx=8)
    button.pack(fill=tk.BOTH)


def make_base_frame(root):
    frame = tk.Frame(root, width=200)
    frame.pack(
        # expand=False,
        expand=True,
        fill=tk.BOTH,
        side=tk.LEFT
    )
    return frame


def make_graph(root) -> GraphBase:
    try:
        graph = GraphBase(root)
    except:
        graph = None
    return graph


def make_named_spinbox(root, name: str):
    """Creates a spinbox with an explaining text to the left.
    This spinbox is scrollable so that the values are easily changed."""
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH)
    label = tk.Label(frame, text=name)
    label.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    spinbox_var = tk.StringVar(frame, value='0.00')
    spinbox = tk.Spinbox(frame, textvariable=spinbox_var, from_=-10000, to=10000, increment=0.5)
    spinbox.bind('<MouseWheel>', _make_scrolling_event(spinbox_var, 1))
    spinbox.pack(side=tk.RIGHT)
    return spinbox_var


def make_combobox(root, interface_variables: dict, selector):
    make_spaced_label(root, f'Select {selector}:')
    combobox = ttk.Combobox(root)
    combobox.pack(fill=tk.BOTH)
    combobox.set('None')
    interface_variables[selector] = ['None']

    def update_combobox():
        combobox['values'] = values = interface_variables[selector]
        if combobox.get() not in values:
            combobox.set(values[0])
        root.after(UPDATE_INTERVAL, update_combobox)

    root.after(UPDATE_INTERVAL, update_combobox)
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
