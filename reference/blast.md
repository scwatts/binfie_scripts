# BLAST reference
## Quick start
First create a database from a FASTA formatted sequence:
```bash
makeblastdb -in reference.fasta -dbtype nucl -out blastdb
```

The run BLAST with a specified list of output metrics/data:
```bash
format_spec='qseqid sseqid qlen slen qstart qend sstart send length evalue bitscore pident nident mismatch gaps'
{
  echo "${format_spec}" | tr ' ' '\t';
  blastn -task blastn -db blast_db -query query.fasta -outfmt "6 ${format_spec}" -max_target_seqs 5000;
} > blast_results.tsv
```
The braces invokes a subshell and runs the wrapped commands, allowing capture of output from the `echo` and `blastn` command
to create a results file that also contains a header.

## NCBI database
To run BLAST against an NCBI database locally, you'll first need to download the desired database. Each database can be
accessed via the FTP here:
```text
ftp://ftp.ncbi.nlm.nih.gov/blast/db/
```

I regularly use the *partially non-redundant nucleotide* which can be download such as:
```bash
mkdir -p nt
for part_num in {01..71}; do
  wget ftp://ftp.ncbi.nlm.nih.gov/blast/db/nt.${part_num}.tar.gz;
done
parallel -j4 'tar -zxvf {} -C nt/' ::: nt/*.tar.gz
```
Depending on your internet connection, downloading can also be parallelised. To use the database you can use:
```bash
blastn -task blastn -db nt/nt -query query.fasta
```
Note that only the database prefix is specified.

## Parallelisation
BLAST has parallelisation built in, however this is widely considered to be somewhat inefficient. Alternatively, input
queries can be split into blocks and processed in parallel. Another consideration is database size - the database must be
loaded into memory and as such may be a limiting factor. Consequently a balance must be found between individual parallelised
instances of BLAST and using the builtin BLAST `--num_threads` options. Below is an example which uses 3 different BLAST
processes each with 8 threads each.
```bash
export cols="qseqid sseqid qlen slen qstart qend sstart send length evalue bitscore pident nident mismatch gaps"
cat large_query_set.fasta | parallel --jobs 3 --recstart '>' --round-robin --pipe --env cols 'blastn -task megablast -num_threads 8 -db nt/nt -outfmt "6 ${cols}"' > ./results.tsv
```
