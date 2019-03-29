#!/usr/bin/env python3
import argparse
import pathlib


class Node:

    def __init__(self, nid, pid, rank):
        self.nid = nid
        self.pid = pid
        self.rank = rank


class Read:

    def __init__(self, rid, sid, tid, fscore, sscore, hlen, qlen, nmatch):
        self.rid = rid
        self.sid = sid
        self.tid = tid
        self.fscore = fscore
        self.sscore = sscore
        self.hlen = hlen
        self.qlen = qlen
        self.nmatch = nmatch


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nodes_fp', required=True, type=pathlib.Path,
            help='nodes.dmp filepath')
    parser.add_argument('--names_fp', required=True, type=pathlib.Path,
            help='names.dmp filepath')
    parser.add_argument('--centrifuge_fp', required=True, type=pathlib.Path,
            help='Centrifuge raw input filepath')

    args = parser.parse_args()
    if not args.nodes_fp.exists():
        parser.error('Input file %s does not exist' % args.nodes_fp)
    if not args.names_fp.exists():
        parser.error('Input file %s does not exist' % args.names_fp)
    if not args.centrifuge_fp.exists():
        parser.error('Input file %s does not exist' % args.centrifuge_fp)
    return args


def main():
    # Get commandline arguments
    args = get_arguments()

    # Parse names file
    names = dict()
    with args.names_fp.open('r') as fh:
        line_token_gen = (line.rstrip('\t|\n').split('\t|\t') for line in fh)
        for line_tokens in line_token_gen:
            if line_tokens[3] != 'scientific name':
                continue
            assert line_tokens[0] not in names
            names[line_tokens[0]] = line_tokens[1]

    # Parse nodes file
    nodes = dict()
    with args.nodes_fp.open('r') as fh:
        line_token_gen = (line.rstrip().split('\t|\t') for line in fh)
        for line_tokens in line_token_gen:
            node = Node(*line_tokens[:3])
            nodes[node.nid] = node

    # Summarise centrifuge file to species rank
    species = dict()
    with args.centrifuge_fp.open('r') as fh:
        line_token_gen = (line.rstrip().split('\t') for line in fh)
        next(line_token_gen)  # skip header
        for read_count, line_tokens in enumerate(line_token_gen, 1):
            read = Read(*line_tokens)
            if read.sid == 'unclassified':
                continue
            # Search upwards through taxa tree to find species rank
            species_tid = find_species_rank(read.tid, nodes)
            if species_tid is None:
                continue
            elif species_tid in species:
                species[species_tid] += 1
            else:
                species[species_tid] = 1

    # Print counts
    print('species', 'taxonomic_id', 'count', 'relab', sep='\t')
    for tid, count in species.items():
        species = names[tid]
        relab = round(count / read_count * 100, 2)
        print(species, tid, count, relab, sep='\t')


def find_species_rank(tid, nodes):
    pid = tid
    cid = None
    while pid != cid:
        node = nodes[pid]
        cid, pid, rank = node.nid, node.pid, node.rank
        if rank == 'species':
            return cid
    return None


if __name__ == '__main__':
    main()
