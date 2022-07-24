import logging
from pathlib import Path

import PySimpleGUI as sg

from calc import calculate_unit_price
from inputs import csv_input
from outputs import export_list_of_labels
from outputs import export_to_csv
from outputs import to_word

log = logging.getLogger(__name__)

in_files = []
user_labels = []


def create_window():
    file_tab_layout = [
        [sg.LBox(values=in_files, size=(80, 10), key='-FILESLB-')],
        [sg.Input(visible=False, enable_events=True, key='-FILE-IN-'), sg.FilesBrowse()],
        ]

    col_left = sg.Col([
        [sg.Text('Zadej cedulku')],
        [sg.Text('Název', size=(15, 1)), sg.InputText(key='name')],
        [sg.Text('Forma', size=(15, 1)), sg.InputText(key='form')],
        [sg.Text('Počet', size=(15, 1)), sg.InputText(key='quantity')],
        [sg.Text('Celková cena', size=(15, 1)), sg.InputText(key='total_price')],
        [sg.Submit(key='-ADD-'), sg.Cancel(key='-CANCEL-')]
        ])
    col_right = sg.Col([
        [sg.LBox(values=user_labels, size=(60, 10), key='-USERLB-')]
        ])
    user_tab_layout = [[col_left, col_right]]

    options_tab_layout = [
        [sg.Text('Možnosti textového exportu:')],
        [sg.Checkbox('číslování', key='numbering', size=(10, 1), default=False)],
        [sg.Checkbox('boxíky', key='checkbox', size=(10, 1), default=False)],
        ]

    template_file = Path('templates/labels_template.docx')
    template_tab_layout = [
        [sg.In(template_file.absolute(), size=(80, 1), key='-TEMPLATE-'), sg.FileBrowse()]
        ]

    layout = [
        [sg.TabGroup([[
            sg.Tab('File', file_tab_layout, tooltip='tip'),
            sg.Tab('User', user_tab_layout),
            sg.Tab('Template', template_tab_layout),
            sg.Tab('Options', options_tab_layout),
            ]])],
        [sg.Button('Create labels', key='-CREATE-')]
        ]

    window = sg.Window('Label maker', layout)
    return window


def update_files(window, values):
    global in_files
    files_box = window['-FILESLB-']
    file_values = values['-FILE-IN-']
    in_files.extend(file_values.split(';'))
    in_files = sorted(set(in_files))
    files_box.update(in_files)


def add_user_label(window, values):
    global user_labels
    labels_box = window['-USERLB-']
    # TODO: validate user input
    item = {
        'name'       : values['name'],
        'form'       : values['form'],
        'unit'       : values['unit'],
        'quantity'   : values['quantity'],
        'total_price': values['total_price'],
        }
    user_labels.append(item)
    labels_box.update(user_labels)


def load_files(files):
    data_from_files = []
    for file in files:
        data_from_files.extend(csv_input(file))
    return data_from_files


def combine_inputs():
    data = []
    data.extend(load_files(in_files))
    data.extend(user_labels)
    return data


def generate_labels(window, values):
    data = combine_inputs()

    # export data for future use
    export_to_csv(data)
    export_list_of_labels(
        data,
        checkbox=values['numbering'],
        numbering=values['checkbox'],
        )
    # intermediate calculations
    calculated_data = calculate_unit_price(data)

    # export
    to_word(calculated_data, values['-TEMPLATE-'])

    sg.Popup('Export finished.')


def gui_main():
    log.info('starting gui app')

    window = create_window()

    event_to_action = {
        '-FILE-IN-': update_files,
        '-ADD-'    : add_user_label,
        '-CREATE-' : generate_labels,
        }

    while True:
        event, values = window.read()
        print(event, values)

        # do actions
        try:
            event_to_action[event](window, values)
        except KeyError:
            print('unknown event')

        if event == sg.WIN_CLOSED:  # always,  always give a way out!
            break

    window.close()

    return 0
