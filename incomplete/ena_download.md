# Downloading reads from ENA
Below is the ENA URL structure for a readset, given an accession. Also shown is a very simple, parallelised method to download the read sets
```bash
export base_url=ftp://ftp.sra.ebi.ac.uk/vol1/fastq;
parallel -j6 --env base_url 'acc={}; wget ${base_url}/${acc:0:6}/00${acc:9:1}/${acc}/${acc}_{1,2}.fastq.gz' :::: <(tail -n+2 run_table.tsv | cut -f10 -d$'\t')
```
