#!/usr/bin/env python3
'''Translate nucleotide FASTA records'''
import argparse
import pathlib


from Bio.Seq import Seq
from Bio.SeqIO.FastaIO import SimpleFastaParser


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_fp', required=True, type=pathlib.Path,
            help='Input nucleotide FASTA filepath')

    args = parser.parse_args()
    if not args.input_fp.exists():
        parser.error('Input file %s does not exist' % args.input_fp)
    return args


def main():
    # Read in data
    args = get_arguments()
    with args.input_fp.open('r') as fh:
        fastas = [(desc, Seq(seq)) for desc, seq in SimpleFastaParser(fh)]

    # Translate and write out
    for desc, seq_obj in fastas:
        print('>', desc, sep='')
        seq = seq_obj.translate(stop_symbol='')
        for line in [seq[i:i+80] for i in range(0, len(seq), 80)]:
            print(line)


if __name__ == '__main__':
    main()
