from utils.constants import lambda_sigma_IMRPhenomD_33
from utils.injection_utils import save_injection_file_ripple
import numpy as np

furthest_point_from_IMRPhenomD = np.array([
    -8951.277000798418,
    -59222.69991418982,
    17293.998601366162,
    -635319.0632809135,
    1819045.400012187,
    52351.502422797945,
    -1165892.7578074015,
    3976064.324245332,
    13877.545634110398,
    -428281.885824933,
    1710863.142700617,

    13481.578808230684,
    369923.2104072197,
    -247516.44856982538,
    5246634.666907884,
    -15587897.82055906,
    -543833.5496407469,
    9889358.939649113,
    -33029853.328761406,
    -193220.39103724685,
    3924961.9956565695,
    -14429087.351155099,
    
    3133.5666282300153,
    -701593.6022990226,
    697015.4860387912,
    -12592280.703721602,
    37847428.436415225,
    1435807.864289309,
    -24028183.830723774,
    79052851.14678615,
    551400.3566888985,
    -9868478.197155943,
    34779296.65685132,
])

mass_ratio = 0.43419265791678147
chi_1 = -0.6
chi_2 = -0.6
total_masses = [20.0, 60.0]
network_snrs = list(range(50, 201, 10)) + [330.0]

for total_mass in total_masses:
    for network_snr in network_snrs:
        save_injection_file_ripple(
            total_mass=total_mass,
            mass_ratio=mass_ratio,
            chi_1=chi_1,
            chi_2=chi_2,
            network_snr=network_snr,
            lambda_sigma=furthest_point_from_IMRPhenomD,
            prefix_injection_name = "flowmc-20240722113944_furthest_point_from_IMRPhenomD"
        )