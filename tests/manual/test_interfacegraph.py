import tkinter as tk

import numpy.random

from SerialPlotter.interfacegraph import Graph, UPDATE_INTERVAL, GraphBase


def main0():
    root = tk.Tk()
    data_x = [_ for _ in range(100)]
    data_y = [_ for _ in range(100)]
    graph = Graph(data_x)
    graph.start(root)

    def update():
        a = data_y[-1]
        for x in data_x:
            y = data_y[x]
            data_y[x - 1] = y
        data_y[-2] = a
        graph.update(data_y)
        graph.draw()
        root.after(UPDATE_INTERVAL, update)

    root.after(UPDATE_INTERVAL, update)
    root.mainloop()


def main():
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()
    graph = GraphBase(frame)

    def update():
        increase[0] += 1
        data = {}
        data.update({'Test': numpy.random.random(increase[0])})
        if increase[0] > 15:
            data.update({'Test1': numpy.random.random(increase[0] - 3)})
        if increase[0] > 20:
            data.update({'Test2': numpy.random.random(increase[0] + 4)})

        graph.plot.set_ylim(0, 1)
        graph.plot.set_xlim(0, increase[0])
        graph.update(data)

    increase = [5]
    button = tk.Button(root, command=update)
    button.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
    # main0()
