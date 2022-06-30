import argparse
import textwrap
from pathlib import Path

from config import setup_logging

setup_logging()

from calc import calculate_unit_price
from inputs import csv_input
from inputs import user_input
from outputs import to_word
from outputs import to_console
from outputs import export_to_csv
from outputs import export_list_of_labels

import logging

log = logging.getLogger(__name__)


def main(argv=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
             Label maker
             --------------------------------
                 Defaults to user input from console.
                 If you wish, you may specify input and template file. 
                 Input must be a csv file, output then a jinja formatted docx.
                 
               - for more info see https://github.com/pyladies-pilsen/label-maker
             ''')
        )
    parser.add_argument(
        '-f',
        '--from-file',
        help='if used, data will be loaded from file',
        action='store_true',
        )
    parser.add_argument(
        '-c',
        '--to-console',
        help='if used, data will be printed to console, may be used to check results',
        action='store_true',
        )
    parser.add_argument(
        '-i',
        '--input-file',
        type=Path,
        default='input/input_data.csv',
        help='specify input data csv file (defaults to: %(default)s)',
        )
    parser.add_argument(
        '-t',
        '--template-file',
        type=Path,
        default='templates/labels_template.docx',
        help='specify template docx file (defaults to: %(default)s)',
        )
    parser.add_argument(
        '--txt-with-numbers',
        help='if used, exported txt file with labels will have numbering',
        action='store_true',
        )
    parser.add_argument(
        '--txt-with-checkbox',
        help='if used, exported txt file with labels will have checkboxes',
        action='store_true',
        )
    args = parser.parse_args(argv)

    log.info(' program start '.center(80, '-'))

    # handle input
    if args.from_file:
        data = csv_input(args.input_file)
    else:
        data = user_input()

    # export data for future use
    export_to_csv(data)
    export_list_of_labels(
        data,
        checkbox=args.txt_with_checkbox,
        numbering=args.txt_with_numbers,
        )

    # intermediate calculations
    calculated_data = calculate_unit_price(data)

    # handle output
    if args.to_console:
        to_console(data)
    else:
        to_word(calculated_data, args.template_file)

    log.info(' program end '.center(80, '-'))


if __name__ == '__main__':
    main()
