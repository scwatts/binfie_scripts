#!/usr/bin/env python3
'''Collate assembly statistics and information encoded in filepaths, which is specific to how I
organise the assemblie data. An example dataset and product of this script is below:

$ tree -L 3 assemblies
assemblies
├── australia_fucp
│   ├── SRR2148855
│   │   ├── 1_illumina_only
│   │   ├── illumina_reads
│   │   ├── SRR2148855.fasta -> 1_illumina_only/assembly.fasta
│   │   ├── sbatch_ui

    ...

│   │   └── slurm_logs
├── france_invasive
│   ├── ERR2794912
│   │   ├── 1_illumina_only
│   │   ├── ERR2794912.fasta -> 1_illumina_only/assembly.fasta
│   │   ├── illumina_reads
│   │   ├── sbatch_ui
│   │   └── slurm_logs

    ...

├── italy_nthi
│   ├── GCA_000833735.1
│   │   ├── 1_public_assembly
│   │   └── GCA_000833735.1.fasta -> 1_public_assembly/GCA_000833735.1_ASM83373v1.fasta

    ...

├── rch
│   ├── M1C111_3
│   │   ├── 1_illumina_only
│   │   ├── illumina_reads
│   │   └── M1C111_3.fasta -> 1_illumina_only/assembly.fasta
│   ├── M1C112_1
│   │   ├── 1_illumina_only
│   │   ├── 2_nanopore_only
│   │   ├── 3_hybrid
│   │   ├── 4_hybrid_fixed
│   │   ├── 5_manual_completion
│   │   ├── illumina_reads
│   │   ├── M1C112_1.fasta -> 5_manual_completion/assembly.fasta
│   │   ├── nanopore_reads
│   │   ├── sbatch_ui
│   │   ├── sbatch_fn
│   │   ├── sbatch_uh
│   │   └── slurm_logs

    ...

└── usa_nthi
    └── GCA_002991485.1
       ├── 1_public_assembly
       └── GCA_002991485.1.fasta -> 1_public_assembly/GCA_002991485.1_ASM299148v1.fasta

$ assembly_stats.py -a
./assemblies/*/*/*.fasta 2>/dev/null | column -t -s$'\t'
study            assembly         type       contig_number  n50      q1       q2       q3        mean     smallest  largest  length
australia_fucp   SRR2148855       illumina   39             273924   202.5    1747     34681.0   46624    105       350913   1818348
france_invasive  ERR2794912       illumina   90             46623    1286.0   8783.0   27505.25  20392    134       187715   1835246
italy_nthi       GCA_000833735.1  public     35             102797   13990.5  38063    90984.0   55303    2710      281898   1935599
rch              M1C111_3         illumina   193            14410    3250     6367     12712     9298     340       45061    1794434
rch              M1C112_1         MANUALFIX  1              1894676  1894676  1894676  1894676   1894676  1894676   1894676  1894676
usa_nthi         GCA_002991485.1  public     144            38638    645.75   3480.5   18864.5   13733    203       123430   1977547'''


import argparse
import pathlib
import math
import statistics
import sys


from Bio.SeqIO.FastaIO import SimpleFastaParser


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--assembly_fps', required=True, nargs='+', type=pathlib.Path,
            help='Input FASTA files as space sperated list')
    args = parser.parse_args()
    for assembly_fp in args.assembly_fps:
        if not assembly_fp.exists():
            parser.error('Input file %s does not exist' % assembly_fp)

    return args


def main():
    args = get_arguments()
    type_dict = {'public_assembly': 'public',
                 'illumina_only': 'illumina',
                 'iontorrent_only': 'ion_torrent',
                 'hybrid_fixed': 'hybrid',
                 'hybrid': 'hybrid'}

    header = ['study', 'assembly', 'type', 'contig_number', 'n50', 'q1', 'q2', 'q3', 'mean', 'smallest', 'largest', 'length']
    print(*header, sep='\t')

    for assembly_fp in args.assembly_fps:
        assembly_type = assembly_fp.resolve().parent.name[2:]
        try:
            assembly_type = type_dict[assembly_type]
        except KeyError:
            # Set ambiguous assembly types to MANUALFIX
            print('WARNING: unable to determine assembly type for', assembly_fp, file=sys.stderr)
            assembly_type = 'MANUALFIX'
        ordered_stats = get_assembly_stats(assembly_fp)
        study = assembly_fp.parents[1].name
        print(study, assembly_fp.stem, assembly_type, *ordered_stats, sep='\t')


def get_assembly_stats(assembly_fp):
    # Get contig lengths
    with assembly_fp.open('r') as f:
        contig_lengths = [len(s) for d, s in SimpleFastaParser(f)]

    # Calculate stats
    contig_number = len(contig_lengths)
    length = sum(contig_lengths)
    smallest = min(contig_lengths)
    largest = max(contig_lengths)
    mean = int(round(statistics.mean(contig_lengths), 0))
    q1, q2, q3 = calculate_quartiles(contig_lengths)

    # n50 func requires more than one contig
    if contig_number > 1:
        n50 = calculate_n50(contig_lengths, length/2)
    else:
        n50 = largest

    # Return ordered stats
    return contig_number, n50, q1, q2, q3, mean, smallest, largest, length


def calculate_quartiles(lengths):
    # Set up
    np = [0.25, 0.50, 0.75]
    x = sorted(lengths)
    n = len(x)
    # Get bounds and quartiles
    indices = [(n - 1) * p for p in np]
    lo = [math.floor(i) for i in indices]
    hi = [math.ceil(i) for i in indices]
    qs = [x[i] for i in lo]
    # Update if required and then return
    for i in range(len(indices)):
        if not indices[i] > lo[i]:
            continue
        h = indices[i] - lo[i]
        qs[i] = (1 - h) * qs[i] + h * x[hi[i]]
    return qs


def calculate_n50(lengths, median):
    csum = 0
    for length in sorted(lengths, reverse=True):
        # If sum exceeds median, return previous length
        if csum > median:
            return prev_length
        # Cumulative sum
        csum += length
        prev_length = length


if __name__ == '__main__':
    main()
