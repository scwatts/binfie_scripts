#!/usr/bin/env python3
'''Subset a RedDog SNP table using a provided list of isolates and filter not variant sites'''


import argparse
import pathlib
import sys


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_fp', required=True, type=pathlib.Path,
            help='Input SNP table')
    parser.add_argument('--sample_names', required=True, nargs='+',
            help='Space-separated list of sample names to retain')
    args = parser.parse_args()
    if not args.input_fp.exists():
        parser.error('Input file %s does not exist' % args.input_fp)
    # We'll need --sample_names as a set later
    args.sample_names = set(args.sample_names)
    return args


def main():
    # Get command line arguments
    args = get_arguments()

    # Process SNP table
    with args.input_fp.open('r') as fh:
        # Set up
        line_token_gen = (line.rstrip().split(',') for line in fh)
        header_tokens = next(line_token_gen)

        # Get column indices - force 'Pos' and 'Ref'
        indices = {0, 1}
        samples_found = set()
        for i, sample in enumerate(header_tokens[2:], 2):
            if sample in args.sample_names:
                indices.add(i)
                samples_found.add(sample)

        # Check for missing samples
        samples_missing = samples_found - args.sample_names
        if len(samples_missing) > 0:
            print('Could not find: ', *samples_missing, sep='\n', file=sys.stderr)
            sys.exit(1)

        # Process data
        header_data = [header_tokens[i] for i in indices]
        print(*header_data, sep=',')
        for line_tokens in line_token_gen:
            # Select only requested columns, check for variance
            data = [line_tokens[i] for i in indices]
            alleles = set(data[1:])
            if '-' in alleles: alleles.remove('-')
            if len(alleles) <= 1:
                continue
            print(*data, sep=',')


if __name__ == '__main__':
    main()
