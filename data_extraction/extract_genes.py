#!/usr/bin/env python3
'''Extract gene nucleotide sequence in FASTA format from genbank records'''
import argparse
import pathlib


import Bio.SeqIO


FASTA_DESC_TEMPL = '>%s_%s %s'


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_fp', required=True, type=pathlib.Path,
            help='Input genabnk filepath')

    args = parser.parse_args()
    if not args.input_fp.exists():
        parser.error('Input file %s does not exist' % args.input_fp)
    return args


def main():
    # Get command line arguments
    args = get_arguments()

    # Iterate genbank records; giving unique name to each gene
    seen_names = dict()
    with args.input_fp.open('r') as fh:
        for genbank_record in Bio.SeqIO.parse(fh, 'genbank'):
            for feature in genbank_record.features:
                if feature.type != 'CDS':
                    continue
                name = str()
                if 'gene' in feature.qualifiers:
                    name = feature.qualifiers['gene'][0]
                elif 'locus_tag' in feature.qualifiers:
                    name = feature.qualifiers['locus_tag'][0]
                elif 'note' in feature.qualifiers:
                    name = feature.qualifiers['note'][0]

                number = int()
                try:
                    seen_names[(name, genbank_record.name)] += 1
                except KeyError:
                    seen_names[(name, genbank_record.name)] = 1
                finally:
                    number = seen_names[(name, genbank_record.name)]

                fasta_desc = FASTA_DESC_TEMPL % (name, number, genbank_record.name)
                sequence = feature.extract(genbank_record).seq
                print(fasta_desc)
                for line in [sequence[i:i+80] for i in range(0, len(sequence), 80)]:
                    print(line)


if __name__ == '__main__':
    main()
