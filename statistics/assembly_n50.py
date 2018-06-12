#!/usr/bin/env python3
'''Calculate n50 from an assembly in FASTA format'''
import argparse
import pathlib


from Bio.SeqIO.FastaIO import SimpleFastaParser


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_fp', required=True, type=pathlib.Path,
            help='Input filepath')

    # Check that input file exists
    args = parser.parse_args()
    if not args.input_fp.exists():
        parser.error('Input file %s does not exist' % args.input_fp)

    return args


def main():
    # Get command line arguments
    args = get_arguments()

    # Read in FASTA sequence and get length
    with args.input_fp.open('r') as fh:
        contig_sizes = sorted((len(seq) for desc, seq in SimpleFastaParser(fh)), reverse=True)

    # Calculate n50
    assembly_size_half = sum((size for size in contig_sizes)) / 2
    running_total = 0
    for size in contig_sizes:
        running_total += size
        if running_total > assembly_size_half:
            print(args.input_fp.stem, size, sep='\t')
            break


if __name__ == '__main__':
    main()
