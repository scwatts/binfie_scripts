#!/usr/bin/env python3
'''The purpose of this script was to read in thousands of FASTA records from a single file and
simulate a perfect read set for each.

This script has some patterns which I often use:
    * temporary directories and files
    * contextlib.ExitStack for handling multiple cm within a single with statement
    * easy pooled threading via concurrent.future
    * basic subprocess command execution
    * simplefastaparser
There is also blocked streaming of FASTA records
'''
import argparse
import concurrent.futures
import contextlib
import math
import pathlib
import tempfile
import subprocess
import sys


from Bio.SeqIO.FastaIO import SimpleFastaParser


WGSIM_TEMPL = 'wgsim -e 0 -d 500 -s 0 -N %s -1 150 -2 150 -r 0 -R 0 -X 0 -A 1 %s %s %s'
GZIP_TEMPL = 'gzip %s %s'


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_fp', required=True, type=pathlib.Path,
            help='Assembly filepath')
    parser.add_argument('--output_dir', required=True, type=pathlib.Path,
            help='Output directory')
    parser.add_argument('--threads', default=1, type=int,
            help='Number of threads')
    args = parser.parse_args()
    if not args.input_fp.exists():
        parser.error('Input file %s does not exist' % args.input_fp)
    if not args.output_dir.exists():
        parser.error('Output directory %s does not exist' % args.output_dir)
    if 32 < args.threads <= 0:
        parser.error('Threads should be between 1 and 32 (probably)')
    return args


def main():
    # Get command line arguments
    args = get_arguments()

    # Process FASTAs
    with contextlib.ExitStack() as stack:
        # Add filehandles to ExitStack cm
        temp_dh = tempfile.TemporaryDirectory(dir=pathlib.Path.cwd())
        temp_dh = stack.enter_context(temp_dh)
        input_fh = stack.enter_context(args.input_fp.open('r'))
        # Stream in records
        block_size = 400
        count = 0
        fasta_gen = SimpleFastaParser(input_fh)
        while True:
            # Using for loop to handle StopIteration gracefully
            fastas = list()
            for i, fasta in enumerate(fasta_gen, 1):
                print(len(fasta[1]))
                fastas.append(fasta)
                if i >= block_size:
                    break
            # Exit while loop once there are no more FASTAs to add
            if not fastas:
                break
            # Collect arguments and then execute
            args_sets = ((fasta, args.output_dir, temp_dh) for fasta in fastas)
            args_sets = zip(*args_sets)
            with concurrent.futures.ProcessPoolExecutor(max_workers=args.threads) as executor:
                [r for r in executor.map(simulate_reads, *args_sets)]
            count += len(fastas)
            print('Finished FASTA %s' % count)


def simulate_reads(fasta, output_dir, temp_dh):
    # Get required number of reads of depth of n
    desc, seq = fasta
    reads_min_cov = math.ceil(5 * len(seq) / 300)
    reads = reads_min_cov if reads_min_cov > 1000 else 1000
    # Write record to file for wgsim
    fasta_fp = None
    with tempfile.NamedTemporaryFile('w', delete=False, dir=temp_dh) as output_fh:
        print('>', desc, sep='', file=output_fh)
        print(seq, file=output_fh)
        fasta_fp = pathlib.Path(output_fh.name)
    # Create reads with wgsim
    forward = output_dir / ('%s_R1.fastq' % fasta_fp.stem)
    reverse = output_dir / ('%s_R2.fastq' % fasta_fp.stem)
    command = WGSIM_TEMPL % (reads, fasta_fp, forward, reverse)
    execute_command(command)
    # Compress reads
    command = GZIP_TEMPL % (forward, reverse)
    execute_command(command)


def execute_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    if result.returncode != 0:
        print('Failed to run command:', result.args, file=sys.stderr)
        print('stdout:', result.stdout, file=sys.stderr)
        print('stderr:', result.stderr, file=sys.stderr)
    return result


if __name__ == '__main__':
    main()
