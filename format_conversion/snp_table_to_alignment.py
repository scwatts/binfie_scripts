#!/usr/bin/env python3
'''Convert a RedDog SNP table to an alignment in FASTA format'''


import argparse
import pathlib


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_fp', required=True, type=pathlib.Path,
            help='Input snp table')
    args = parser.parse_args()
    if not args.input_fp.exists():
        parser.error('Input file %s does not exist' % args.input_fp)

    return args


def main():
    # Get command line arguments
    args = get_arguments()

    with args.input_fp.open('r') as fh:
        header_tokens = fh.readline().rstrip().split(',')
        isolates = header_tokens[1:]

        # Group SNP data by isolate
        line_token_gen = (line.rstrip().split(',') for line in fh)
        position_snp_gen = (lts[1:] for lts in line_token_gen)
        isolate_snp_gen = zip(*position_snp_gen)

        # Print out SNP alignments
        for isolate, snps in zip(isolates, isolate_snp_gen):
            print('>', isolate, sep='')
            for line in [snps[i:i+80] for i in range(0, len(snps), 80)]:
                print(*line, sep='')


if __name__ == '__main__':
    main()
