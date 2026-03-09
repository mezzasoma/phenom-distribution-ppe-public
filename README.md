# phenom-distribution-ppe-public

This repository contains the scripts and environment setup used to perform the parameter estimation for "Impact of numerical-relativity waveform calibration on parametrized post-Einsteinian tests".

## Quick start
1. Clone this repository on both the cluster and your laptop. It is designed to run independently in each location:
   - Laptop: intended for file generation, code development, and postprocessing (Jupyter notebook is available too, using the IPython kernel created during installation).
   - Cluster: intended for running the parameter-estimation jobs across multiple nodes (SLURM scheduler is required).
2. Populate `config_example.yaml` and rename it to `config.yaml`.
3. From within the repository `phenom-distribution-ppe-public`, create the conda environment by running
    ```
    bash conda/create_phenom_distribution_ppe.sh 
    ```
    This can take several minutes. Ignore the dependency conflict `pesummary 1.3.1 requires lalsuite>7.11` if it shows up.
4. Activate the newly-installed conda environment `phenom-distribution-ppe` with
    ```
    conda activate phenom-distribution-ppe
    ```
5. Download the noise power spectral density (O5) for LIGO and Virgo, then generate the injection and prior files by running
    ```
    cd data/analysis/bilby-inference
    python create_psd.py
    python create_injection.py
    python create_prior.py
    ```
6. Start parameter estimation with `bilby` using the launch script. For example:
    ```
    bash ../../../scripts/bilby-inference/launch_parallel_bilby.sh configuration/inj-ripple-rec-ripple-ppe.ini prior/ripple_delta_at_IMRPhenomD_total_mass_60.0_mass_ratio_0.434_no_ppe.prior injection/ripple_flowmc-20240722113944_furthest_point_from_IMRPhenomD_total_mass_60.0_mass_ratio_0.434_chi_1_-0.60_chi_2_-0.60_SNR_100.0.inj
    ```
    See usage notes with 
    ```
    bash ../../../scripts/bilby-inference/launch_parallel_bilby.sh --help
    ```
7. To generate corner plots, use
    ```
    python postprocess_bilby_run.py
    ```
## Requirements
- Laptop: Anaconda 2024.06
- Cluster: Anaconda 2024.06, SLURM 25.05.5, Open MPI v5.0.1