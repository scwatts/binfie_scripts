'''Code from hicap showing showing examples of:
    * using a wider help formatter
    * supressing nonessential arguments (with optional --help_all)
    * collecting version from __init__.py or similar
'''
import argparse
import pathlib
import sys


from . import __version__


class WideHelpFormatter(argparse.HelpFormatter):

    def __init__(self, *args, **kwargs):
        terminal_width = shutil.get_terminal_size().columns
        help_width = min(terminal_width, 140)
        super().__init__(*args, **kwargs, max_help_position=help_width, width=help_width)


def get_args():
    # Parsers
    parser_parent = argparse.ArgumentParser(formatter_class=WideHelpFormatter, add_help=False)
    parser_files = parser_parent.add_argument_group('File input and output')
    parser_params = parser_parent.add_argument_group('Search parameters')
    parser_other = parser_parent.add_argument_group('Other')

    # Inputs and outputs
    database_dir = pathlib.Path(__file__).parent / 'database'
    model_path = pathlib.Path(__file__).parent / 'model/prodigal_hi.bin'
    parser_files.add_argument('-q', '--query_fp', required=True, type=pathlib.Path,
                              help='Input FASTA query')
    parser_files.add_argument('-o', '--output_dir', required=True, type=pathlib.Path,
                              help='Output directory')
    parser_files.add_argument('-d', '--database_dir', required=False, type=pathlib.Path, default=database_dir,
                              help='Directory containing locus database. [default: %s]' % database_dir)
    parser_files.add_argument('-m', '--model_fp', required=False, type=pathlib.Path, default=model_path,
                              help='Path to prodigal model. [default: %s]' % model_path)
    parser_files.add_argument('-s', '--full_sequence', required=False, action='store_true',
                              help='Write the full input sequence out to the genbank file rather '
                              'than just the region surrounding and including the locus')

    # Parameters
    parser_params.add_argument('--gene_coverage', default=0.80, type=float,
                               help='Minimum percentage coverage to consider a single gene complete. [default: 0.80]')
    parser_params.add_argument('--gene_identity', default=0.70, type=float,
                               help='Minimum percentage identity to consider a single gene complete. [default: 0.70]')
    parser_params.add_argument('--broken_gene_length', default=60, type=int,
                               help='Minimum length to consider a broken gene. [default: 60]')
    parser_params.add_argument('--broken_gene_identity', default=0.80, type=float,
                               help='Minimum percentage identity to consider a broken gene. [default: 0.80]')

    # Other
    parser_other.add_argument('--threads', type=int, default=1, help='Threads to use for BLAST+. [default: 1]')
    parser_other.add_argument('--log_fp', type=pathlib.Path, help='Record logging messages to file')
    parser_other.add_argument('--debug', action='store_const', dest='log_level', const=logging.DEBUG,
                              default=logging.INFO, help='Print debug messages')
    parser_other.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__),
                              help='Show version number and exit')
    parser_other.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    parser_other.add_argument('--help_all', action='store_true', help='Display extended help')

    # Change behaviour of help display
    quick_help_args = ('--query_fp', '--output_dir', '--version', '--help', '--help_all')
    if '--help_all' in sys.argv[1:]:
        parser_parent.print_help()
        sys.exit(0)
    for arg in parser_parent._actions:
        if not any(qarg in arg.option_strings for qarg in quick_help_args):
            arg.help = argparse.SUPPRESS

    # Glob for database files
    args = parser_parent.parse_args()
    args.gene_database_fps = [fp for fp in args.database_dir.glob('*fasta') if '1016' not in fp.name]
    args.is_database_fp = args.database_dir / 'IS1016V6.fasta'
    return args
