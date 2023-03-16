import threading
import tkinter as tk
from tkinter import ttk
from typing import Dict, List

from .filehandler import json_load, json_save
from .interfacegraph import GraphBase
from .program import SerialHandler, SerialThread

UPDATE_INTERVAL = 500


class InterfaceVariables:
    tk_vars: Dict[str, tk.Variable] = {}
    tk_data: Dict[str, list] = {}
    graph_data: Dict[str, any] = {}
    settings = json_load()
    extra_settings = {}
    arduino = SerialHandler()
    running = threading.Event()

    def __init__(self):
        thread_serial = SerialThread(self.running, self.arduino)
        self.threads: List[threading.Thread] = [thread_serial]

    def import_settings(self):
        settings = self.settings = json_load()
        for key, value in settings.get('tk_vars').items():
            if key not in self.tk_vars:
                continue
            self.tk_vars[key].set(value)
        for key, data in settings.get('tk_data').items():
            # if key not in self.tk_data:
            #     continue
            self.tk_data[key] = data
        for key, data in settings.get('graph_data').items():
            # if key not in self.graph_data:
            #     continue
            self.graph_data[key] = data
        if 'filters' in settings:
            self.extra_settings['filters'] = settings['filters']
        if 'recorder' in settings:
            self.extra_settings['recorder'] = settings['recorder']

    def export_settings(self):
        version = '1.0'
        tk_vars = {key: value.get() for key, value in self.tk_vars.items()}
        tk_data = {'graph': self.tk_data['graph']}
        gr_data = {'state': self.graph_data['state']}
        settings = {
            'version': version,
            'tk_vars': tk_vars,
            'tk_data': tk_data,
            'graph_data': gr_data,
        }
        settings.update(self.extra_settings)
        json_save(settings)

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

