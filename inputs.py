"""Inputs.

Take input and return data in format of list[dict]


Example of output:
[
    {
    'name': 'Bromhexin',
    'form': 'gtt'
    'unit': 'ml',
    'quantity': 100,
    'total_price': 194.0,
    },
    {
    'name': 'Bromhexin',
    'unit': 'ml',
    'quantity': 100,
    'total_price': 194.0,
    },
    {...},
    {...},
]

"""
import csv
import itertools
import logging

log = logging.getLogger(__name__)

VALID_FORMS = {
    'gtt' : "ml",
    'sir' : "ml",
    'sol' : "ml",
    'pst' : "ks",
    'tbl' : "ks",
    'cps' : "ks",
    'ung' : "g",
    'crm' : "g",
    'supp': "ks",
    'spr' : "ml",
    'grg' : "ml",
    'dos' : "ks",
    'sac' : "ks",
    'pulv': "g",
    "pasta" : "ml",
    "sada" : "ks",
    "šamp" : "ml",
    "eff" : "ks",
    "spec" : "g",
    "gel" : "g",
    "gum" : "ks",
    "empl" : "ks",
    "ZP" : "ml",
}


def positive_float(string):
    num = float(string)
    if not 0 < num < 10_000:
        raise ValueError('Smí být jen od 0 do 10 000.')
    return num


def better_input(question, value_type, valid_options=None):
    """Validate input based on the passed value type.

    Upon error continuously prompt user for correct answer.
    """

    while True:
        try:
            answer = value_type(input(f'- {question}{valid_options if valid_options is not None else ""}: '))

            if valid_options and answer not in valid_options:
                raise ValueError('neni z povolených hodnot')

            if not answer:
                raise ValueError('Nepovolujeme prázné hodnoty a nuly.')

        except ValueError:
            print('Špatně zadaná hodnota')

        else:
            return answer


def user_input():
    """Take input from user.

    Exmaple input:
        Nazev: Bromhexin
        Forma: gtt
        Jednotky: ml
        Pocet: 100
        Celkova cena: 194
        -- další? [a/n]:
    """
    label_counter = itertools.count(start=1)
    entries = []
    while True:
        print(f'Cedulka číslo: {next(label_counter):>3}')
        item = {
            'name'       : better_input('Název', str),
            'form'       : better_input('Forma', str, valid_options=VALID_FORMS.keys()),
            'quantity'   : better_input('Počet', int),
            'total_price': better_input('Celková cena', positive_float),
        }
        item["unit"] = VALID_FORMS.get(item["form"], "")
        entries.append(item)

        next_q = input('-- další? [a/n]: ')
        if next_q == 'n':
            return entries


def csv_input(input_file):
    """Load data from csv."""
    log.info('loading data from csv file')
    with open(input_file, encoding='UTF-8') as file:
        reader = csv.DictReader(file, quoting=csv.QUOTE_NONNUMERIC)
        data = list(reader)
    for item in data:
        item["unit"] = VALID_FORMS.get(item["form"], "")
    # TODO: validate data, remove and notify about the unvalid
    return data
