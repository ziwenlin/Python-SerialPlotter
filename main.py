import tkinter as tk
from tkinter import ttk

from interfacebuilder import make_base_frame, make_spaced_label, make_labeled_entry, make_button, make_spacer, \
    make_updateable_label


class InterfaceVariables:
    info_data = {}


def build_interface():
    top = tk.Tk()
    interface = InterfaceVariables()
    panel_port_selector(top, interface)

    top.data = interface
    return top


def panel_port_selector(base, interface: InterfaceVariables):
    def start_command():
        pass

    def stop_command():
        pass

    def restart_command():
        pass

    def refresh_command():
        pass

    frame = make_base_frame(base)
    make_spaced_label(frame, 'Configurator')
    make_spacer(frame, 10)
    make_spaced_label(frame, 'Selectable ports:')
    make_updateable_label(frame, interface.info_data, 'ports')

    make_spacer(frame, 10)
    entry_port = make_labeled_entry(frame, 'Serial port:')
    make_button(frame, start_command, 'Start')
    make_button(frame, stop_command, 'Stop')
    make_button(frame, restart_command, 'Restart')


if __name__ == '__main__':
    root = build_interface()
    root.mainloop()
