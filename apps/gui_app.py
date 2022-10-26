import logging
from pathlib import Path

import PySimpleGUI as sg

from calc import calculate_unit_price
from inputs import VALID_FORMS
from inputs import csv_input
from outputs import export_list_of_labels
from outputs import export_to_csv
from outputs import to_word

log = logging.getLogger(__name__)


class GUIApp:

    def __init__(self):
        self.in_files = []
        self.user_labels = []
        self.event_to_action = {
            '-FILE-IN-': self.update_files,
            '-ADD-'    : self.add_user_label,
            '-CREATE-' : self.generate_labels,
            '-TABLE-'  : self.display_table_delete_popup,
        }
        self.table_header_to_key = {
            'name'       : 'Název',
            'form'       : 'Forma',
            'unit'       : 'Jednotky',
            'quantity'   : 'Počet',
            'total_price': 'Celková cena',
            'unit_price' : 'Cena ks',
        }

    def __enter__(self):
        self.window = self.create_window()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.window.close()

    def __eat_events__(self):
        """Eats falsely fired events
        NOTE: https://github.com/PySimpleGUI/PySimpleGUI/issues/4268
        """
        while True:
            event, values = self.window.read(timeout=0)
            if event == '__TIMEOUT__':
                break
        return

    def run(self):
        while True:
            event, values = self.window.read()
            log.debug((event, values))

            if event == sg.WIN_CLOSED:  # always,  always give a way out!
                break

            # do actions
            try:
                self.event_to_action[event](values)
                self.__eat_events__()
            except KeyError:
                log.exception('unknown event')

    def create_window(self):

        def _file_tab():
            return [
                [sg.LBox(values=self.in_files, size=(80, 10), key='-FILESLB-')],
                [sg.Input(visible=False, enable_events=True, key='-FILE-IN-'),
                 sg.FilesBrowse(button_text='Vyber soubor')],
            ]

        def _user_tab():
            col_left = sg.Col(
                [
                    [sg.Text('Název', size=(15, 1)), sg.InputText(key='name', do_not_clear=True)],
                    [sg.Text('Forma', size=(15, 1)), sg.InputText(key='form', do_not_clear=True)],
                    [sg.Text('Počet', size=(15, 1)), sg.InputText(key='quantity', do_not_clear=True)],
                    [sg.Text('Celková cena', size=(15, 1)), sg.InputText(key='total_price', do_not_clear=True)],
                    [sg.Submit(button_text='Přidat', key='-ADD-'), sg.Cancel(button_text='Zrušit', key='-CANCEL-')]
                ]
            )
            col_right = sg.Col(
                [
                    [sg.Table(
                        headings=list(self.table_header_to_key.values()),
                        values=[],
                        max_col_width=25,
                        auto_size_columns=True,
                        justification='right',
                        num_rows=10,
                        key='-TABLE-',
                        enable_events=True,
                        expand_x=False,
                        expand_y=False,
                        vertical_scroll_only=False,
                    )]
                ]
            )
            return [[col_left, col_right]]

        def _options_tab():
            return [
                [sg.Text('Možnosti textového exportu:')],
                [sg.Checkbox('číslování', key='numbering', size=(10, 1), default=False)],
                [sg.Checkbox('boxíky', key='checkbox', size=(10, 1), default=False)],
            ]

        def _template_tab():
            template_file = Path('templates/labels_template.docx')
            return [
                [sg.In(template_file.absolute(), size=(80, 1), key='-TEMPLATE-'), sg.FileBrowse()]
            ]

        layout = [
            [sg.TabGroup(
                [[
                    sg.Tab('Ze souboru', _file_tab()),
                    sg.Tab('Ručně', _user_tab()),
                    sg.Tab('Template', _template_tab()),
                    sg.Tab('Možnosti', _options_tab()),
                ]]
            )],
            [sg.Button(button_text='vytvořit cedulky', key='-CREATE-')]
        ]

        window = sg.Window('Label maker', layout)
        return window

    def display_table_delete_popup(self, values):
        event, _ = sg.Window(
            '',
            [
                [sg.Text('Smazat řádek?')],
                [sg.B('Ano'), sg.B('Ne')],
            ]
        ).read(close=True)
        row_num = values['-TABLE-'][0]
        if event == 'Ano':
            self.user_labels.pop(row_num)
            self.update_user_table()

    def update_files(self, values):
        files_box = self.window['-FILESLB-']
        file_values = values['-FILE-IN-']
        self.in_files.extend(file_values.split(';'))
        self.in_files = sorted(set(self.in_files))
        files_box.update(self.in_files)

    def _write_to_table(self, data):
        labels_table = self.window['-TABLE-']
        labels_table.update(data)

    def _prepare_data_for_table(self, data):
        calculated_data = calculate_unit_price(data)
        # add unit
        for item in calculated_data:
            item["unit"] = VALID_FORMS.get(item["form"], "")
        # transform to list of lists
        return [
            [label[k] for k, v in self.table_header_to_key.items()]
            for label in self.user_labels
        ]

    def update_user_table(self):
        data_for_table = self._prepare_data_for_table(self.user_labels)
        self._write_to_table(data_for_table)

    def add_user_label(self, values):
        # TODO: add validation
        item = {
            'name'       : values['name'],
            'form'       : values['form'],
            'quantity'   : int(values['quantity']),
            'total_price': int(values['total_price']),
        }
        self.user_labels.append(item)
        self.update_user_table()

    def load_files(self, files):
        data_from_files = []
        for file in files:
            data_from_files.extend(csv_input(file))
        return data_from_files

    def combine_inputs(self):
        data = []
        data.extend(self.load_files(self.in_files))
        data.extend(self.user_labels)
        return data

    def generate_labels(self, values):
        data = self.combine_inputs()

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

    with GUIApp() as gui:
        gui.run()

    return 0
