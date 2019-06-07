# Bowtie2
## Quick start
Index a reference:
```bash
bowtie2-build reference/reference.fasta indices/reference.fasta
```

Mapping reads to reference:
```bash
bowtie2 -X 2000 -x indices/reference.fasta -1 reads/sample_R1.fastq.gz -2 reads/sample_R2.fastq.gz -S output/sample.sam
```

## Practical example with many samples
The previous section provides basic commands for mapping. Here I provide an example in which we map many samples and extract
summary information from the resulting data.

Generating indices for several references:
```bash
mkdir 1_indices
parallel 'bowtie2-build {} 1_indices/{/}' ::: references/*fasta
```

Mapping samples to all references, removing unmapped reads, converting to BAM and sorting:
```bash
mkdir 2_bams
forward_reads=reads/*R1.fastq.gz
indices=$(find references/ -type f -name '*fasta' -printf '1_indices/%f\n')
parallel 'forward={1}; \
          index={2}; \
          reverse=${forward/R1/R2}; \
          forward_basename={1 /}; \
          index_basename={2 /}; \
          sample=${forward_basename/_R1.fastq.gz/}; \
          ref=${index_basename/.fasta/}; \
          output=2_bams/${sample}_${ref}.bam; \
          bowtie2 -X 2000 -x ${index} -1 ${forward} -2 ${reverse} | samtools view -uF4 | samtools sort > ${output}' ::: ${forward_reads} ::: ${indices}
```
The parallel command above will map all combinations of read pairs and indices, using all available cores. This effect is
achieved using two input command line argument specifiers (denoted by :::) - one for read sets and one for indices.

The bowtie2 command first maps the reads, then converts the SAM data in stdout to BAM while removing unmapped reads.
Following this, the BAM file is sorted and written to disk.

Once we have the sorted BAM files, we do many types of analyses. Here I'll just grab the depth and coverage for each BAM
file:
```bash
# Function to calculate average depth and percent of positions that meet a minimum depth
function depth_coverage() {
  bam_fp=${1};
  depth_depth=$(samtools depth -a ${bam_fp} | awk '{sum += $3} END {print sum/NR}' || echo 0);
  depth_min_pct=$(samtools depth -a ${bam_fp} | awk '{if ($3 >= 5) { count += 1 }} END {print 100 * count/NR}' || echo 0);
  bam_fn=${bam_fp##*/};
  sample=${bam_fn/.bam/};
  echo -e "${sample}\t${depth_depth}\t${depth_min_pct}";
}

# Export function and run with parallel
export -f depth_coverage;
parallel depth_coverage ::: 2_bams/*bam;
```
