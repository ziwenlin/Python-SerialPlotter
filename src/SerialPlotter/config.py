line_filter = {
    'state': 1,
    'name': 'Line',
}

filters = {
    'filters': [line_filter]
}

connection = {
    'device': 'None',
    'keep': 0,
}

communication = {
    'command': '',
    'show': 0,
    'keep': 0,
}

recorder = {
    'file_name': 'Unnamed',
    'auto_save': 0,
    'file_append': 0,
    'file_overwrite': 0,
    'data_dir': './data/',
    'backup_dir': './backup/',
}

formatter = {
    'decimal': 'Comma',
    'delimiter': 'Semicolon',
}

settings = {
    'version': '2.0',
    'filters': filters,
    'connection': connection,
    'communication': communication,
    'recorder': recorder,
    'format': formatter
}
