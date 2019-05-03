import argparse
import shutil


from . import __version__


class WideHelpFormatter(argparse.HelpFormatter):

    def __init__(self, *args, **kwargs):
        terminal_width = shutil.get_terminal_size().columns
        help_width = min(terminal_width, 140)
        super().__init__(*args, **kwargs, max_help_position=help_width, width=help_width)


def get_args():
    parser = argparse.ArgumentParser(formatter_class=WideHelpFormatter, add_help=False)
    parser.add_argument('-n', '--number', required=True, type=float, help='Input number')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__),
            help='Show version number and exit')
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    return parser.parse_args()
