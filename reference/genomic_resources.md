# Genomics data sources
Here are some quick links and simple examples data acquisition.

## Resources
### AMR
* NCBI AMR: [bioproject](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA313047) (isolates enumerated in pathogen detection)
* Beta-lactamase database: [http://bldb.eu/](http://bldb.eu/)

### NCBI databases and reports
* Assembly reports: [ftp://ftp.ncbi.nih.gov/genomes/ASSEMBLY_REPORTS/](ftp://ftp.ncbi.nih.gov/genomes/ASSEMBLY_REPORTS/)
* BLAST databases: [ftp://ftp.ncbi.nlm.nih.gov/blast/db/](ftp://ftp.ncbi.nlm.nih.gov/blast/db/)
* Genbank: [ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/234/745/GCF_001234745.1_7065_7_79/](ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/234/745/GCF_001234745.1_7065_7_79/)
* Pathogen detection: [ftp://ftp.ncbi.nih.gov/pathogen/](ftp://ftp.ncbi.nih.gov/pathogen/)
* Plasmids: [ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/plasmid](ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/plasmid)
* Refseq: [ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/001/234/745/GCA_001234745.1_7065_7_79/](ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/001/234/745/GCA_001234745.1_7065_7_79/)
* SRA records: [ftp://ftp.ncbi.nih.gov/sra/sra-instant/reads/ByRun/sra/SRR/SRR123/SRR1234780/](ftp://ftp.ncbi.nih.gov/sra/sra-instant/reads/ByRun/sra/SRR/SRR123/SRR1234780/)
* Taxonomy [ftp://ftp.ncbi.nih.gov/pub/taxonomy/](ftp://ftp.ncbi.nih.gov/pub/taxonomy/)
* BLAST executables: [ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
* tbl2asn executables: [ftp://ftp.ncbi.nih.gov/toolbox/ncbi_tools/converters/by_program/tbl2asn/](ftp://ftp.ncbi.nih.gov/toolbox/ncbi_tools/converters/by_program/tbl2asn/)

### Metagenomics
* MGnify: [https://www.ebi.ac.uk/metagenomics/](https://www.ebi.ac.uk/metagenomics/)


## Read downloading
### ENA
This is the ENA URL structure for a readset, given an accession. Also shown is a very simple, parallelised method to download the read sets.
```bash
export base_url=ftp://ftp.sra.ebi.ac.uk/vol1/fastq;
parallel -j6 --env base_url 'acc={}; wget ${base_url}/${acc:0:6}/00${acc:9:1}/${acc}/${acc}_{1,2}.fastq.gz' :::: <(tail -n+2 run_table.tsv | cut -f10 -d$'\t')

# Check that gzips are valid
parallel 'if ! gzip -t {} 1>/dev/null 2>&1; then echo {}; fi' ::: ./*gz
```
The run_table.tsv was downloaded from the SRA run selector and in the 10th column contained the run accession.


### NCBI
NCBI stores all read data in the SRA format. To obtain FASTQ sequence data, you must first download the SRA file and then use
`fastq-dump`. Downloading and processing of SRA files can be done concurrently using `fastq-dump` however I find doing this
step-wise manually to be much faster and more reliable. Here is a recent example:
```bash
# Create output directories
mkdir -p 1_read_sets/{sra,fastq}

# Download SRA files using accessions located in data/sra_accessions.txt
parallel --jobs 20 --colsep $'\t' 'acc={}; outfile=1_read_sets/sra/${acc}.sra; \
                                   if [[ ! -s ${outfile} ]]; then \
                                     url_base=ftp://ftp-trace.ncbi.nih.gov/sra/sra-instant/reads/ByRun/sra; \
                                     curl -s ${url_base}/${acc:0:3}/${acc:0:6}/${acc}/${acc}.sra > ${outfile}; \
                                   fi;' :::: data/sra_accessions.txt

# Find any SRA files that have failed to download or are otherwise corrupt
find 1_read_sets/sra -size -10k
parallel 'if ! vdb-validate {} 1>/dev/null 2>&1; then echo {}; fi' ::: $(find 1_read_sets/sra/ -name '*sra')

# Extract read data as FASTQ
parallel 'outdir=1_read_sets/fastq/; \
          file_count=$(find ${outdir} -name "{/.}*" | wc -l); \
          if [[ ${file_count} -lt 2 ]]; then \
            if vdb-validate {} 1>/dev/null 2>&1; then \
              fastq-dump --outdir ${outdir} --gzip --split-files --readids {}; \
            fi; \
          fi;' ::: 1_read_sets/sra/*.sra

# Check that gzips are valid
parallel 'if ! gzip -t {} 1>/dev/null 2>&1; then echo {}; fi' ::: $(find 1_read_sets/fastq/ -name '*gz')
```

## Assembly download
Collecting assemblies from NCBI has been simplified somewhat with a recently added feature - when searching the `assembly`
database you will find a 'Download Assemblies' button just under the search bar. This is useful as you can query for a
bioproject, species, etc and download the complete assembly database.
