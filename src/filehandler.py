import json
import csv
import datetime
from pathlib import Path

SETTINGS_FILE = 'settings.json'

CSV_FOLDER = './data/'
CSV_DELIMITER = ','
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
        js = json.dumps(settings)
        jsf.write(js)


def csv_writer(file):
    return csv.writer(file, delimiter=CSV_DELIMITER)


def csv_save_auto(data):
    csv_save_append(DATE_TIME, data)


def csv_save_write(file_name, data):
    if len(file_name) <= 1:
        file_name = 'Unnamed'
    if not Path(CSV_FOLDER).exists():
        Path(CSV_FOLDER).mkdir()
    with open(CSV_FOLDER + file_name + CSV_EXTENSION, 'w', newline='') as file:
        writer = csv_writer(file)
        writer.writerows(data)
    return True


def csv_save_append(file_name, data):
    if len(file_name) <= 1:
        file_name = 'Unnamed'
    if not Path(CSV_FOLDER).exists():
        Path(CSV_FOLDER).mkdir()
    with open(CSV_FOLDER + file_name + CSV_EXTENSION, 'a', newline='') as file:
        writer = csv_writer(file)
        writer.writerows(data)
    return True


def csv_save_create(file_name, data):
    if len(file_name) <= 1:
        file_name = 'Unnamed'
    if not Path(CSV_FOLDER).exists():
        Path(CSV_FOLDER).mkdir()
    try:
        with open(CSV_FOLDER + file_name + CSV_EXTENSION, 'x', newline='') as file:
            writer = csv_writer(file)
            writer.writerows(data)
    except FileExistsError:
        return False
    return True
