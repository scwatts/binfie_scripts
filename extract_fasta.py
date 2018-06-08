#!/usr/bin/env python3
'''Extract FASTA records where description contains word(s) in a specified list'''


import argparse
import pathlib


from Bio.SeqIO.FastaIO import SimpleFastaParser


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_fp', required=True, type=pathlib.Path,
            help='Input FASTA file')
    parser.add_argument('--contains', required=True, nargs='+',
            help='Description contains')
    parser.add_argument('--case_sensitive', action='store_true',
            help='Perform case insensitive matching')

    args = parser.parse_args()
    if not args.input_fp.exists():
        parser.error('Input file %s does not exist' % args.input_fp)
    return args


def main():
    args = get_arguments()

    # Set case sensitivity once outside of main loop
    if args.case_sensitive:
        words = args.contains
        fasta_contains_word = lambda desc, words: any(w in desc for w in words)
    else:
        words = [w.lower() for w in args.contains]
        fasta_contains_word = lambda desc, words: any(w in desc.lower() for w in words)

    # Iterate records and print if criteria met
    with args.input_fp.open('r') as fh:
        for desc, seq in SimpleFastaParser(fh):
            if not fasta_contains_word(desc, words):
                continue
            print('>', desc, sep='')
            for line in [seq[i:i+80] for i in range(0, len(seq), 80)]:
                print(line)


if __name__ == '__main__':
    main()
