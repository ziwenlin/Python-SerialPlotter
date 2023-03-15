import datetime
import json
import os
import tkinter as tk
import webbrowser
from pathlib import Path

import pandas

SETTINGS_FILE = 'settings.json'

CSV_BACKUP = './backup/'
CSV_FOLDER = './data/'

CSV_DELIMITER = ','
CSV_DECIMAL = '.'
CSV_EXTENSION = '.csv'

DATE_FORMAT = "%Y-%m-%d_%H_%M"
DATE_TIME = datetime.datetime.now().strftime(DATE_FORMAT)


def json_load(settings=None):
    if settings is None:
        settings = {}
    try:
        with open(SETTINGS_FILE, 'r+') as json_file:
            js = json.load(json_file)
        settings.update(js)
    except FileNotFoundError:
        json_save(settings)
    return settings


def json_save(settings: dict):
    with open(SETTINGS_FILE, 'w+') as jsf:
        js = json.dumps(settings, indent=1)
        jsf.write(js)


def open_directory(path):
    if path[0] in '.':
        program_path = os.getcwd()
        path = path.replace('.', program_path, 1)
    webbrowser.open(path)


def ask_directory():
    path = tk.filedialog.askdirectory(initialdir='./')
    if path == '':
        return path
    program_path = os.getcwd().replace('\\', '/')
    path = path.replace(program_path, '.') + '/'
    return path


def csv_writer(file_path, data, mode):
    dataframe = pandas.DataFrame(data)
    dataframe.to_csv(file_path, mode=mode,
                     decimal=CSV_DECIMAL, sep=CSV_DELIMITER,
                     index=False, header=False)
    return dataframe


def csv_save_auto(data):
    if not Path(CSV_BACKUP).exists():
        Path(CSV_BACKUP).mkdir()
    file_path = CSV_BACKUP + DATE_TIME + CSV_EXTENSION
    csv_writer(file_path, data, 'a')
    return True


def csv_save_write(file_name, data):
    if len(file_name) <= 1:
        file_name = 'Unnamed'
    if not Path(CSV_FOLDER).exists():
        Path(CSV_FOLDER).mkdir()
    file_path = CSV_FOLDER + file_name + CSV_EXTENSION
    csv_writer(file_path, data, 'w')
    return True


def csv_save_append(file_name, data):
    if len(file_name) <= 1:
        file_name = 'Unnamed'
    if not Path(CSV_FOLDER).exists():
        Path(CSV_FOLDER).mkdir()
    file_path = CSV_FOLDER + file_name + CSV_EXTENSION
    csv_writer(file_path, data, 'a')
    return True


def csv_save_create(file_name, data):
    if len(file_name) <= 1:
        file_name = 'Unnamed'
    if not Path(CSV_FOLDER).exists():
        Path(CSV_FOLDER).mkdir()
    file_path = CSV_FOLDER + file_name + CSV_EXTENSION
    try:
        csv_writer(file_path, data, 'x')
    except FileExistsError:
        return False
    return True
