# NCBI taxonomy reference
The maintainers of taxonomy database from NCBI regularly dump the database to text files which can be accessed from the NCBI
FTP. The database dump is particularly useful when wanting to relate one taxonomic rank to another. This document will show
how to download database dump, describe useful files, and demonstrate how to iterate the taxonomic tree.

## Downloading
The latest dump of the database can be accessed such as:
```bash
mkdir -p data/
wget -P data/ ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
tar -zxvf data/taxdump.tar.gz -C data/
```

There are also historical dumps which have been archived. They can be found in:
```bash
ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump_archive/
```

## Contents
Below I have summarised information relevant to my usages and more detailed information for the taxonomy database dump can be
found in this README:
```bash
curl -s ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump_readme.txt | less
```

### nodes.dmp
The nodes file contains a tree of taxonomy data. The following fields are typically of most use:
| column    | name              | description                   |
| ---       | ---               | ---                           |
| 1         | tax_id            | node id                       |
| 2         | parent tax_id     | parent node id                |
| 3         | rank              | taxonomic rank of this node   |

### names.dmp
This file contains name information for each taxonomic rank and simply uses `node id` key to map related data.
| column    | name          | description           |
| ---       | ---           | ---                   |
| 1         | tax_id        | node id               |
| 2         | name_txt      | name                  |
| 3         | unique name   | unique name variant   |
| 4         | name class    | name type             |

Often the desired entries are those that have a `name class` of `scientific name`.

## How to use
### Traversing the tree
One common task is to traverse the taxonomic tree and extract name information at certain nodes. Here are a set of examples
to read and traverse the data:
```python
class Node:

    def __init__(self, nid, pid, rank):
        self.nid = nid
        self.pid = pid
        self.rank = rank


def read_nodes(nodes_fp):
    nodes = dict()
    with nodes_fp.open('r') as fh:
        line_token_gen = (line.rstrip().split('\t|\t') for line in fh)
        for line_tokens in line_token_gen:
            node = Node(*line_tokens[:3])
            nodes[node.nid] = node
    return nodes


def read_names(names_fp):
    names = dict()
    with names_fp.open('r') as fh:
        line_token_gen = (line.rstrip('\t|\n').split('\t|\t') for line in fh)
        for node_id, node_name, node_uname, node_type in line_token_gen:
            if node_type != 'scientific name':
              continue
            assert node_id not in names
            names[node_id] = node_name
    return names


def traverse_to_genus(taxid, nodes):
    pid = taxid
    cid = None
    while pid != cid:
        node = nodes[pid]
        cid, pid, rank = node.nid, node.pid, node.rank
        if rank == 'genus':
            return cid
    return None


def complete_example(names_fp, nodes_fp, taxid_input):
    # Read in data
    names = read_names(names_fp)
    nodes = read_nodes(nodes_fp)
    # Traverse until we reach rank of genus or root
    taxid_result = traverse_to_genus(taxid_input, nodes)
    # Print associated info
    name_input = names[taxid_input]
    if taxid_result:
        message = 'Input taxid %s (%s) has a genus node taxid of %s (%s)'
        name_result = names[taxid_result]
        print(message % (taxid_input, name_input, taxid_result, name_result))
    else:
        print('Could not find genus level node for %s (%s)' % (taxid_input, name_input))

```

### Species summarisation
The above approach is effective in find the species node for a given node. However if performance is a primarily concern,
then use of `categories.dmp` from the `taxcat.tar.gz` dump is recommended. This file contains all ranks below species with
mappings to the species node - such information enables species identification by a single set check and then a dictionary
lookup.

### Other thoughts
Preprocessing the taxonomic tree to determine which nodes are above a desired rank could also greatly improve performance
(depending on query size of course).
