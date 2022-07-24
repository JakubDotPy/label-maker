import logging

import PySimpleGUI as sg

log = logging.getLogger(__name__)


def gui_main():
    log.info('starting gui app')

    file_tab_layout = [[sg.T('This is tab to select files.')]]

    user_tab_layout = [[sg.T('This is tab for user input.')]]

    layout = [
        [sg.TabGroup([[sg.Tab('File', file_tab_layout, tooltip='tip'), sg.Tab('User', user_tab_layout)]])],
        [sg.Button('Read')]
        ]

    window = sg.Window('Label maker', layout, default_element_size=(12, 1))

    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:  # always,  always give a way out!
            break

    window.close()
