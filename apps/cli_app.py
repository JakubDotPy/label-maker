import argparse
import logging
import textwrap
from pathlib import Path

from calc import calculate_unit_price
from inputs import csv_input
from inputs import user_input
from outputs import export_list_of_labels
from outputs import export_to_csv
from outputs import to_console
from outputs import to_word

log = logging.getLogger(__name__)


def setup_argparse():
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

    # inputs
    parser.add_argument(
        '-u',
        '--user',
        help='if used, user will provide data using console',
        action='store_true',
        )
    parser.add_argument(
        '-f',
        '--file',
        nargs='*',
        help='specify input data csv files (defaults to: %(default)s)',
        )

    # outputs
    parser.add_argument(
        '-c',
        '--to-console',
        help='if used, data will be printed to console, may be used to check results',
        action='store_true',
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

    return parser


def cli_main(argv):
    parser = setup_argparse()
    args = parser.parse_args(argv)

    # handle input
    data = []
    # load files
    for file in args.file or []:
        file_data = csv_input(file)
        log.info(f'- loaded {len(file_data)} labels from {file}')
        data.extend(file_data)
    # load user input
    if args.user:
        user_data = user_input()
        log.info(f'- loaded {len(user_data)} labels from user')
        data.extend(user_data)

    if not data:
        log.warning('No data were provided, exiting.')
        return 2

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

    return 0
