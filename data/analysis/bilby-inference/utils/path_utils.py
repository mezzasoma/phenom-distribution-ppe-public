import os
from pathlib import Path
import yaml

def create_and_set_outdir(subfolder_name):
    """
    Create an output directory under the current working directory.

    Parameters:
    subfolder_name (str): Name of the subdirectory to create inside 'outdir'.
    """
    outdir = os.path.join(os.getcwd(), 'outdir', subfolder_name)
    os.makedirs(outdir, exist_ok=True)
    return outdir

def get_path_to_config_file():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    cfg_path = str(repo_root / "config.yaml")
    return cfg_path

def get_path_to_repo_on_cluster():
    cfg_path = get_path_to_config_file()

    with Path(cfg_path).open("r") as f:
        config = yaml.safe_load(f) or {}

    return config["path_to_repo_on_cluster"]

def get_path_to_flowmc_gaussian_prior_on_laptop():
    cfg_path = get_path_to_config_file()

    with Path(cfg_path).open("r") as f:
        config = yaml.safe_load(f) or {}

    return config["path_to_flowmc_gaussian_prior_on_laptop"]

def get_path_to_flowmc_delta_prior_on_laptop():
    cfg_path = get_path_to_config_file()

    with Path(cfg_path).open("r") as f:
        config = yaml.safe_load(f) or {}

    return config["path_to_flowmc_delta_prior_on_laptop"]

def get_path_to_bilby_runs_on_laptop():
    cfg_path = get_path_to_config_file()

    with Path(cfg_path).open("r") as f:
        config = yaml.safe_load(f) or {}

    return config["path_to_bilby_runs_on_laptop"]