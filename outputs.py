import csv
import itertools
import logging
from pathlib import Path

from docxtpl import DocxTemplate

from calc import enumerate_keys
from calc import merge_page_data
from calc import prepare_rows
from calc import split_to_page_size

WORD_OUTPUT_NAME = 'generated_labels'
OUTPUT_FOLDER = 'output'

log = logging.getLogger(__name__)


def to_console(data):
    """Print labels to console.

    Only for testing purposes.
    """
    from textwrap import dedent
    from string import Template

    log.info('outputting to console')

    template = Template(
        dedent(
            """\
                ┌──────────────────────────────┐
                │${name}│
                │${form_qty_unit}│
                │                              │
                │${price}│
                │                              │
                │${bottom_row}│
                └──────────────────────────────┘
                """
            )
        )

    data = prepare_rows(data)
    for label in data:
        centered = {k: f'{v:^30}' for k, v in label.items()}
        filled = template.substitute(centered)
        print(filled)


def to_word(data, template):
    """Output the label data to word files."""
    log.info('output to word started')

    # prepare output folder
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

    # reformat the dicts for replace
    data = prepare_rows(data)

    # prepare paginated data
    page_splitted_data = split_to_page_size(data)

    # for each page
    for page_num, page_data in enumerate(page_splitted_data, start=1):
        # open new template for each page
        doc = DocxTemplate(template)

        # prepare the numbers for replacing
        replace_ready = enumerate_keys(page_data)
        context = merge_page_data(replace_ready)
        # make the replacement
        log.debug(f'replacing page {page_num}')
        doc.render(context=context)

        # save to new file
        filename = f'{page_num:02}_{WORD_OUTPUT_NAME}.docx'
        log.debug(f'saving to file {filename}')
        doc.save(Path(OUTPUT_FOLDER) / filename)

    log.info('output to word finished')


def export_to_csv(data):
    """Output the inserted data to csv file for future use."""
    log.info('exporting input data to csv')

    with open('output/exported_labels.csv', 'w', newline='', encoding='UTF-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)

        writer.writeheader()
        for label in data:
            writer.writerow(label)


def export_list_of_labels(data, checkbox=False, numbering=False):
    """Export list of labels for reference."""
    log.info(f'exporting list of labels {"- with checkboxes" if checkbox else ""}')

    num_labels = len(data)

    # use same format of top row
    rows = [
        '{name} {form} {quantity:.0f} {unit}'.format(**label)
        for label in data
        ]
    if numbering:
        label_counter = itertools.count(start=1)
        rows = [f'{next(label_counter):>3}. - {row}' for row in rows]
    if checkbox:
        rows = [f'[ ] - {row}' for row in rows]

    with open('output/exported_label_names.txt', 'w', encoding='UTF-8') as file:
        file.write(f'Seznam cedulek - celkem {num_labels}\n')
        file.write('-' * 80 + '\n')
        file.write('\n'.join(rows))
