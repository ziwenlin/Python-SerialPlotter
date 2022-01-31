from main import build_interface

if __name__ == '__main__':
    root, interface = build_interface()
    interface.start_threads()
    root.mainloop()
    interface.stop_threads()
    interface.export_settings()