# Rscript argument parsing
```R
args = commandArgs(trailingOnly=TRUE)
if (length(args) != 4) {
stop('Check number of arguments')
}
# Copy args into new variables for legibility
het_vcf <- args[1]
hom_vcf <- args[2]
genome_length <- as.numeric(args[3])
title <- args[4]
```
