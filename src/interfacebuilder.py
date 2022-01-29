import tkinter as tk

from interfacegraph import GraphBase


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
    label = tk.Label(root, textvariable=label_var, anchor='sw', padx=5, height=1)
    label.pack(fill=tk.BOTH)


def make_spacer(root, size):
    spacer = tk.Frame(root, height=size)
    spacer.pack()


def make_button(root, command, name):
    button = tk.Button(root, text=name, command=command, height=2, anchor='w', padx=8)
    button.pack(fill=tk.BOTH)


def make_base_frame(root):
    frame = tk.Frame(root, width=1600)
    frame.pack(
        expand=True,
        fill=tk.BOTH,
        side=tk.LEFT
    )
    return frame

def make_graph(root):
    frame = make_base_frame(root)
    graph = GraphBase(frame)
    return graph


def _make_scrolling_event(tk_var: tk.Variable, multiplier=1):
    def scrolling(event):
        value = tk_var.get()
        try:
            value = float(value) + multiplier * (event.delta / 120)
            tk_var.set(f'{value:.2f}')
        except:
            pass

    return scrolling
