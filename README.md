# General bioinformatics
Useful code and references for everyday bioinformatics-related tasks

## Contents
* **data_extraction**
    * `extract_fasta.py`: extract FASTA records where description has match in word list
    * `extract_genes.py`: extract DNA sequences from GenBank records
    * `translate_nucleotide.py`: translate nucleotide sequence
* **format_conversion**
    * `emboss_distmat_to_ts.py`: convert EMBOSS distance matrix to square matrix in TSV format
    * `snp_table_to_alignment.py`: convert SNP table (RedDog output) to a SNP alignment
    * `subset_snp_table.py`: subset SNP table (RedDog output) with a provided sample list
* **incomplete**
    * `ena_download.md`: bare example of downloading readsets from ENA given an accession
* **project_skeletons**
    * `cpp_autotools/`: basic C++ project using autotools build system
    * `python_cpp_extension/`: python C++ extension
    * `python_package/`: pure python package
* **reference**
    * `bash_commands.md`: some useful commands and snippets
    * `blast.md`: command line BLAST basics - includes blocking and parallelisation
    * `bowtie2.md`: bowtie2 basics
    * `misc_utility.md`: miscellaneous snippets related to bioinformatics
    * `ncbi_eutils.md`: eutils API for pull NCBI database information
    * `ncbi_ftp.md`: URLs to useful files and data
    * `ncbi_taxonomy.md`: usage of NCBI taxonomy database
    * `slurm_sbatch.md`: efficient job submission using sbatch
* **statistics**
    * `assembly_stats.py`: calculate N50 and other statistics of assemblies
* **summarisation**
    * `centrifuge_species.py`: summarise centrifuge counts to species rank
* **unsorted**
    * `argument_parsing.py`: wide formatting, non-essential argument suppression
    * `asyncio_basic.py`
    * `asyncio_requeue.py`
    * `blast.py`: functions for BLAST from python with typed results parsing
    * `debugging_slow_processes.py`: example of debugging very slow process, quickly
    * `dependencies_check.py`
    * `plot_timeline_piecharts.R`: ggplot timelines, dodging select elements, ggplot2 modification, unscaled piecharts
    * `render_assembly_graphs_and_stitch.txt`: using bandage and imagemagick to render assembly graph comparisons
    * `rscript_argument_parsing.md`: very basic Rscript argument parser
    * `scrape_imngs_lists.py`: HTTP session, token management, getpass
    * `simulate_reads.py`: blocked streaming of FASTA records, concurrent.futures threading, contextlib, tempfile
    * `urllib2_download.py`
* **visulisation**
    * `colour_palettes.svg`: some reference colour palettes for figures
    * `gg_scaling_and_log10p_transform.R`: scale ggtree plots and create custom ggplot2 transforms
    * `mlst_mst.R`: minimum spanning tree from MLST data (SRST2 output)
