#!/usr/bin/env python3
'''Convert an EMBOSS distmat to an ordered square matrix'''
import argparse
import pathlib


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--matrix', required=True, type=pathlib.Path,
            help='Path to EMBOSS distance matrix')
    parser.add_argument('-t', '--otu_ids', required=True, type=pathlib.Path,
            help='File containing order of OTUs')

    args = parser.parse_args()
    if not args.matrix.exists():
        parser.error('Input file %s does not exist' % args.matrix)
    if not args.otu_ids.exists():
        parser.error('Input file %s does not exist' % args.otu_ids)

    return args


def main():
    # Get commandline arguments
    args = get_arguments()

    # Read in OTU ids
    with args.otu_ids.open('r') as f:
        ordered_otu_ids = [line.rstrip() for line in f]

    # Read in distmat matrix
    with args.matrix.open('r') as f:
        # Skip irrelevant data
        for i in range(8):
            f.readline()

        # Read in all lines
        raw_data = [line.strip().split('\t') for line in f]

    # Get OTU ids
    row_info = [row[-1].split() for row in raw_data]
    otu_ids, row_number = zip(*row_info)

    # Get representation of just the rows
    rows = [raw_row[:-2] for raw_row in raw_data]
    elements = [el.strip() for row in rows for el in row if el != '0.00']

    # Construct symmetric matrix
    element_count = len(rows)

    print('#OTU ID', *ordered_otu_ids, sep='\t')
    for otu_id_one in ordered_otu_ids:
        # Print row OTU ids
        print(otu_id_one, end='')

        for otu_id_two in ordered_otu_ids:
            # If we're on diagonal, print 0.00 and continue to next element
            if otu_id_one == otu_id_two:
                print('\t0.00', sep='', end='')
                continue

            # Get indices of OTUs
            i = otu_ids.index(otu_id_one) + 1
            j = otu_ids.index(otu_id_two) + 1

            # Order indices so that we stay in the upper triangle
            index_one, index_two = sorted([i, j])
            index = linear_index(index_one, index_two, element_count)

            # Print data
            print('\t', elements[index], sep='', end='')

        # Print new line
        print('\n', end='')


def linear_index(i, j, n):
    return int((j + (i - 1) * n - (i * (i + 1)) / 2) - 1)


if __name__ == '__main__':
    main()
