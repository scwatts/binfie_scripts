# SLURM sbatch submission
Running the same command or process on many inputs can be automated using BASH. AS sbatch extends functionality of a
typically BASH script, we can leverage argument parsing within the scripts. Alternatively you may use sed to modify the
sbatch script and pass that to sbatch.

## Submission with script arguments
Here is an example were I want to run an Rscript on many input sets. The different inputs and outputs are defined by BASH
variables within the sbatch script.
```bash
#!/bin/bash
#SBATCH --account=js66
#SBATCH --job-name=SAMPLE_allelic_status
#SBATCH --partition=com,comp,m3a,m3c,m3d,m3h,m3i
#SBATCH --qos=normal
#SBATCH --time=0-00:05:00
#SBATCH --mem=4096
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1-1
#SBATCH --output=slurm_logs/SAMPLE_allelic_status-%j.log
#SBATCH --error=slurm_logs/SAMPLE_allelic_status-%j.log
# Software
module load R/3.5.2-openblas

# Task
./scripts/run_plotter.R output/${sample}/ ${vcf_dir} ${sample} ${ref_id} ${ref_fp};
```

To automate job submission you can use a for loop and iterate inputs.
```bash
# Export variables for sbatch script
export vcf_dir=reddog_output/vcf
export ref_id=NC_000907
export ref_fp=reddog_output/hi_rdkw_20.gbk

# Submit jobs
samples="sample_1 sample_2 sample_3 sample_4 sample_5"
for sample in ${samples}; do
  export sample;
  mkdir -p output/${sample};
  jobname=${sample}_allelic_status;
  log_fp=slurm_logs/${sample}_allelic_status-%j.log;
  sbatch --job-name=${jobname} --output=${log_fp} --error=${log_fp} scripts/sbatch_plot;
done
```

Note that you cannot supply BASH variables to `#SBATCH` directives but instead must set them when calling `sbatch`.


# Submission with sed
Rather than using BASH variables as above, instead here we use placeholders for each variable that are then substituted for
the desired values with sed.
```bash
#!/bin/bash
#SBATCH --account=js66
#SBATCH --job-name=ctrfg_SAMPLE
#SBATCH --partition=com,comp,m3a,m3c,m3d,m3h,m3i
#SBATCH --qos=normal
#SBATCH --time=0-01:00:00
#SBATCH --mem=16384
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1-1
#SBATCH --output=slurm_logs/ctrfg_SAMPLE-%j.log
#SBATCH --error=slurm_logs/ctrfg_SAMPLE-%j.log
# Software
module load centrifuge/1.0.4-beta

# Task
centrifuge --threads 1 -k 1 -x /projects/js66/data/databases/centrifuge/default/p+h+v -1 FORWARD -2 REVERSE -S OUTRAW --report-file OUTREP
```

As previously seen, we use a for loop to automate submission. Here we also only submit if output files are not present or
empty.
```bash
forward_fps=./data/reads/*R1*fastq.gz
for forward in ${forward_fps}; do
  # Get sample details
  reverse=${forward/R1/R2};
  basename=${forward##*/};
  sample=${basename/_R1.fastq.gz/}

  # Get output filepaths
  output_raw=1_centrifuge/${sample}_raw.tsv;
  output_report=1_centrifuge/${sample}_report.tsv;

  # Submit job only if output files do not exist
  if [[ ! -s "${output_report}" ]]; then
    sed -e 's#SAMPLE#'${sample}'#g' -e 's#FORWARD#'${forward}'#' \
        -e 's#REVERSE#'${reverse}'#' -e 's#OUTRAW#'${output_raw}'#' \
        -e 's#OUTREP#'${output_report}'#' \
        scripts/sbatch_centrifuge | sbatch;
  fi;
done
```
