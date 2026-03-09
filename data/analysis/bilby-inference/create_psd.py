from utils.psd_utils import get_psd, crop_psd_to_inspiral_only

get_psd()

total_masses = [20.0, 60.0]
for total_mass in total_masses:
    crop_psd_to_inspiral_only(total_mass=total_mass)