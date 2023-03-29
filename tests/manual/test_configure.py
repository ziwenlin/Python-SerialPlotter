import tkinter

from SerialPlotter.manager import TaskInterface
from SerialPlotter.panels.configure import Controller

root = tkinter.Tk()
frame = tkinter.Frame(root)
frame.pack(fill='both', expand=True)

interface = TaskInterface()
controller = Controller(frame, interface)

root.mainloop()
