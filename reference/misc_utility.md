# Miscellaneous utility
Here are snippets that have varying degrees of utility related mostly related to bioinformatics


## Collect assemblies
This process is specific to the directory structure I have used to organise assemblies. A single sample may have different
types of assemblies (short read, long read, hybrid) and may also under go multiple iterations of assembly. Samples are
organised by project and all sample assemblies are co-located within the appropriate directory. Here is an example:

```text
assemblies/
├── rch/M1C056_2/
│   ├── 1_illumina_only/
│   └── illumina_reads/
├── rch/M1C079_1/
│   ├── 1_illumina_only/
│   ├── 2_nanopore_only/
│   ├── 3_hybrid/
│   ├── illumina_reads/
│   └── nanopore_reads/
├── sanger/DC7331102
│   └── 1_public_assembly/
└── sanger/Hi1008
    └── 1_public_assembly/
```

Both sanger and rch are project names and each assembly directory is prefixed with a digit (e.g. 3\_hybrid/) - indicating a
'better' assembly. To always have the 'best' assembly accessible in a standardised way, I place a symlink in the sample
directory with the name `${sample}.fasta`. Here is a simple BASH loop that can do this well-enough and should be run in the
`assemblies/` directory:

```bash
for project in *; do
  for dir in ${project}/*; do
    sample=${dir##*/};
    assembly_dir=$(find ${dir} -maxdepth 1 -type d | grep "${sample}/[0-9]" | sort -n | tail -n1);
    # Try to find an appropriate assembly file
    unset file;
    if [[ -s ${assembly_dir}/assembly.fasta ]]; then
      file=assembly.fasta;
    elif [[ -s ${assembly_dir}/contigs.fasta ]]; then
      file=contigs.fasta;
    elif [[ -s $(find ${assembly_dir} -name '*.fasta') ]]; then
      file=$(find ${assembly_dir} -name '*.fasta' -printf "%f\n");
    elif [[ -s $(find ${assembly_dir} -name '*.fa') ]]; then
      file=$(find ${assembly_dir} -name '*.fa' -printf "%f\n");
    fi;
    # Alert if none were found
    if [[ -z ${file+x} ]]; then
      echo ${assembly_dir} assembly not found or resolvable;
      continue;
    fi;
  # Symlink
  assembly_dirname=${assembly_dir##*/};
  ln -s ${assembly_dirname}/${file} ${dir}/${sample}.fasta;
  done;
done
```
