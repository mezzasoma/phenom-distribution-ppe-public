import os
import requests
import numpy as np
from io import StringIO
from glob import glob
from utils.constants import solar_mass_in_seconds

def get_psd():
    """
    Download and save the noise power spectral density (PSD) of O5 detectors from 
    https://dcc.ligo.org/LIGO-T2000012/public
    """
    psd_dir = os.path.join(os.getcwd(), 'psd')
    os.makedirs(psd_dir, exist_ok=True)

    urls = {
        'AplusDesign': 'https://dcc.ligo.org/public/0165/T2000012/002/AplusDesign.txt',
        'avirgo_O5high_NEW': 'https://dcc.ligo.org/public/0165/T2000012/002/avirgo_O5high_NEW.txt'
    }

    for name, url in urls.items():
        response = requests.get(url)
        response.raise_for_status()
        data = np.loadtxt(StringIO(response.text))
        data[:, 1] = np.square(data[:, 1], dtype=np.float64)

        out_path = os.path.join(psd_dir, f"{name}_psd.txt")
        np.savetxt(out_path, data, fmt='%.18e', delimiter=' ')
        print(f"{name} saved.")

def crop_psd_to_inspiral_only(total_mass=20.0):
    """
    Crop PSDs to inspiral only (maximum_frequency = 0.018/total_mass) and save them.
    PSD values above maximum_frequency are set to 1000.
    """
    psd_dir = os.path.join(os.getcwd(), 'psd')
    maximum_frequency = 0.018 / (total_mass * solar_mass_in_seconds)

    paths_to_psds = glob(os.path.join(psd_dir, '*_psd.txt'))

    if not paths_to_psds:
        raise FileNotFoundError(
            f"No PSD files ending in '_psd.txt' found in '{psd_dir}'. "
            "Run `get_psd()` to download the PSD files."
        )

    for path_to_psd in paths_to_psds:
        data = np.loadtxt(path_to_psd)
        frequency, psd = data[:, 0], data[:, 1]

        psd[frequency > maximum_frequency] = 1000.0

        new_path_to_psd = f"{path_to_psd.rsplit('.', 1)[0]}_total_mass_{total_mass}.txt"
        np.savetxt(new_path_to_psd, np.column_stack((frequency, psd)), fmt='%.18e')
        print(f"Inspiral-only PSD saved.")

def crop_psd_to_maximum_frequency(maximum_frequency=48.0):
    """
    Crop PSDs to a given maximum_frequency (in Hz) and save them.
    PSD values above maximum_frequency are set to 1000.
    """
    psd_dir = os.path.join(os.getcwd(), 'psd')
    paths_to_psds = glob(os.path.join(psd_dir, '*_psd.txt'))

    if not paths_to_psds:
        raise FileNotFoundError(
            f"No PSD files ending in '_psd.txt' found in '{psd_dir}'. "
            "Run `get_psd()` to download the PSD files."
        )

    for path_to_psd in paths_to_psds:
        data = np.loadtxt(path_to_psd)
        frequency, psd = data[:, 0], data[:, 1]

        psd[frequency > maximum_frequency] = 1000.0

        new_path_to_psd = f"{path_to_psd.rsplit('.', 1)[0]}_f_max_{maximum_frequency}.txt"
        np.savetxt(new_path_to_psd, np.column_stack((frequency, psd)), fmt='%.18e')
        print(f"Frequency-cropped PSD saved.")