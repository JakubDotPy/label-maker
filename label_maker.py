import sys

from config import setup_logging

setup_logging()

from apps.cli_app import cli_main
from apps.gui_app import gui_main

import logging

log = logging.getLogger(__name__)


def main(argv=None):
    log.info(' program start '.center(80, '-'))
    try:
        args = sys.argv[1:]
        if not args:
            log.info('GUI MODE')
            exit_code = gui_main()
        else:
            log.info('CLI MODE')
            exit_code = cli_main(argv)

        log.info(' program end '.center(80, '-'))
    except Exception as e:
        log.exception(e)
        exit_code = 2
    finally:
        return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
