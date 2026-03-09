#!/bin/bash

function help() {
  cat << EOF
Usage: bash launch_parallel_bilby.sh <ini_file> <prior_file> <injection_dict>

The script takes in three arguments:
  1. a parallel_bilby configuration (.ini) file, devoid of prior dictionary and injection dictionary
  2. a prior file (.prior)
  3. an injection dictionary (.inj)

The script then does the following:
1. check that the number of arguments passed is three. If not, exit with error.
2. create a folder in \$HOME/scratch/phenom-distribution-ppe/data/raw/ whose name is the UTC timestamp
   in the format YYYYMMDDHHMMSS at the time the script is executed.
   This is the unique identifier of that run.
3. copy the .ini, .prior, .inj files under \$HOME/scratch/phenom-distribution-ppe/data/raw/YYYYMMDDHHMMSS/ and run
   parallel_bilby_generation on them
4. if successful, run
       bash outdir/submit/bash_label.sh
  where label is some global label that is parsed from the .ini file. Examples are
  label = test-run or label = production-run
EOF
}


if [ $# -ne 3 ]; then
  help
  exit 1
fi

ini_file="$1"
prior_file="$2"
injection_dict="$3"

project=phenom-distribution-ppe
pathtorun=$HOME/scratch/$project/data/raw/$(date -u +%Y%m%d%H%M%S)

if [ -d "$pathtorun" ]; then
    sleep 1s
    echo "Wait 1 second before starting the next job, to not overwrite the directory"
    pathtorun=$HOME/scratch/$project/data/raw/$(date -u +%Y%m%d%H%M%S)
fi

echo "run folder: $pathtorun"
mkdir -p $pathtorun

cp "$ini_file" "$pathtorun"
copied_ini_filename=$(basename "$ini_file")
copied_ini_file="$pathtorun/$copied_ini_filename"

cp "$prior_file" "$pathtorun"
copied_prior_filename=$(basename "$prior_file")
copied_prior_file="$pathtorun/$copied_prior_filename"

cp "$injection_dict" "$pathtorun"
copied_injection_filename=$(basename "$injection_dict")
copied_injection_dict="$pathtorun/$copied_injection_filename"

cd $pathtorun

source $HOME/.bashrc

conda activate phenom-distribution-ppe

cat $copied_injection_dict >> $copied_ini_file

parallel_bilby_generation --prior-file=$copied_prior_file $copied_ini_file

label=$(awk '$1=="label"{print $3}' $copied_ini_file)

# The following line modifies the analysis script to add the "--verbose" option to the mpirun command.
# This change is necessary because, with Open MPI 5.0, mpirun mistakenly interprets 
# parallel_bilby's options (e.g. --nlive) as its own, unless "--verbose" is specified.
sed -i 's/^mpirun /mpirun --verbose /' outdir/submit/analysis_${label}_0.sh

bash outdir/submit/bash_${label}.sh