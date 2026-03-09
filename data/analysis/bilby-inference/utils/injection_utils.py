from utils.constants import lambda_sigma_IMRPhenomD_33
import numpy as np
import os

def get_shortest_safe_duration(mass_1, mass_2, chi_1, chi_2, minimum_frequency=10.0):
    """
    Adapted from 
    https://github.com/bilby-dev/bilby/blob/0985f75c664786e21cc4f662d4f12fe181b1a536/bilby/gw/detector/__init__.py#L8
    Use `SimInspiralChirpTimeBound` defined in
    https://lscsoft.docs.ligo.org/lalsuite/lalsimulation/_l_a_l_sim_inspiral_8c_source.html#l04999
    and not `SimIMRPhenomDChirpTime` defined in
    https://lscsoft.docs.ligo.org/lalsuite/lalsimulation/_l_a_l_sim_i_m_r_phenom_d_8c_source.html#l00597
    because `SimInspiralChirpTimeBound` gives a more conservative duration estimate.
    """
    from lal import MSUN_SI
    from lalsimulation import SimInspiralChirpTimeBound

    chirp_time = SimInspiralChirpTimeBound(
        minimum_frequency, mass_1 * MSUN_SI, mass_2 * MSUN_SI,
        chi_1, chi_2)

    safe_duration = max(2**(int(np.log2(chirp_time)) + 1), 4)
    return safe_duration

def get_snr_and_safe_duration_from_injection(injection_dict, minimum_frequency, maximum_frequency):
    """
    Compute the network SNR and the safe duration using the default IMRPhenomD.
    """
    import bilby
    from bilby.gw.detector import InterferometerList
    import logging
    logging.getLogger("bilby").setLevel(logging.ERROR)
    
    mass_1 = injection_dict['mass_1']
    mass_2 = injection_dict['mass_2']
    total_mass = injection_dict['total_mass']
    chi_1 = injection_dict['chi_1']
    chi_2 = injection_dict['chi_2']
    trigger_time = injection_dict['geocent_time']
    reference_frequency = injection_dict['reference_frequency']

    sampling_frequency = 2 * maximum_frequency # 512 if maximum_frequency is 256

    duration = get_shortest_safe_duration(mass_1, mass_2, chi_1, chi_2, minimum_frequency)

    detectors = ['H1', 'L1', 'V1']
    ifos = InterferometerList(detectors)

    psd_paths = {
        'H1': f'./psd/AplusDesign_psd_total_mass_{total_mass:.1f}.txt',
        'L1': f'./psd/AplusDesign_psd_total_mass_{total_mass:.1f}.txt',
        'V1': f'./psd/avirgo_O5high_NEW_psd_total_mass_{total_mass:.1f}.txt'
    }

    for ifo in ifos:
        psd_file = psd_paths[ifo.name]
        ifo.power_spectral_density = bilby.gw.detector.PowerSpectralDensity(psd_file=psd_file)
        ifo.minimum_frequency = minimum_frequency # this is essential!
        ifo.set_strain_data_from_zero_noise(
            sampling_frequency=sampling_frequency,
            duration=duration,
            start_time=trigger_time - duration + 2
        )
        

    waveform_arguments = dict(
        waveform_approximant='ripple',
        reference_frequency=reference_frequency,
        minimum_frequency=minimum_frequency,
        maximum_frequency= maximum_frequency,
        catch_waveform_errors=True
    )
    
    waveform_generator = bilby.gw.waveform_generator.WaveformGenerator(
    duration=duration,
    sampling_frequency=sampling_frequency,
    frequency_domain_source_model=bilby.gw.source.ripple_binary_black_hole,
    waveform_arguments=waveform_arguments
    )

    for i, value in enumerate(lambda_sigma_IMRPhenomD_33):
        injection_dict[f'lambda_sigma_{i}'] = np.float64(value)

    ifos.inject_signal(parameters=injection_dict, waveform_generator=waveform_generator)

    optimal_snrs = {}
    for ifo in ifos:
        frequency_domain_strain = waveform_generator.frequency_domain_strain(injection_dict)
        signal = ifo.get_detector_response(frequency_domain_strain, injection_dict)
        frequency_array = waveform_generator.frequency_array
        psd = ifo.power_spectral_density
        snr_squared = bilby.gw.utils.inner_product(signal, signal, frequency_array, psd)
        optimal_snrs[ifo.name] = np.sqrt(snr_squared)
        
    network_snr = np.sqrt(np.sum([snr**2 for snr in optimal_snrs.values()]))

    return network_snr, duration

def get_injection_dictionary_and_safe_duration_ripple(total_mass = 20.0, mass_ratio=0.4, chi_1=0.0, chi_2=0.0, network_snr=100.0, lambda_sigma=lambda_sigma_IMRPhenomD_33):
    assert mass_ratio <= 1.0, "Error: mass_ratio must be less than or equal to 1.0"
    assert -1.0 <= chi_1 <= 1.0, "Error: chi_1 must be between -1 and 1"
    assert -1.0 <= chi_2 <= 1.0, "Error: chi_2 must be between -1 and 1"

    mass_1 = total_mass / (1.0 + mass_ratio)
    mass_2 = total_mass * mass_ratio / (1.0 + mass_ratio)
    chirp_mass = total_mass * mass_ratio**(3.0/5.0) * (1.0 + mass_ratio)**(-6.0/5.0)
    trigger_time = 1126259642.413
    reference_frequency = 10
    minimum_frequency = 10 
    maximum_frequency = 256
    injection_dict = {
        'mass_1': mass_1,
        'mass_2': mass_2,
        'theta_jn': 0.4,
        'luminosity_distance': 100.0,
        'psi': 2.659,
        'ra': 1.375,
        'dec': -1.2108,
        'phase': 1.3,
        'geocent_time': trigger_time,
        'reference_frequency': reference_frequency,
        'chi_1': chi_1,
        'chi_2': chi_2,
        'mass_ratio': mass_ratio,
        'chirp_mass': chirp_mass,
        'total_mass': total_mass
    }
    
    network_snr_at_luminosity_distance_100, duration = get_snr_and_safe_duration_from_injection(injection_dict, minimum_frequency, maximum_frequency)
    
    to_be_injected_luminosity_distance = 100.0 * (network_snr_at_luminosity_distance_100/network_snr)
    injection_dict['luminosity_distance'] = to_be_injected_luminosity_distance

    assert np.allclose(get_snr_and_safe_duration_from_injection(injection_dict, minimum_frequency, maximum_frequency)[0], network_snr) 

    for i, value in enumerate(lambda_sigma):
        injection_dict[f'lambda_sigma_{i}'] = np.float64(value)
    
    return injection_dict, duration

def save_injection_file_ripple(
    total_mass=20.0,
    mass_ratio=0.4,
    chi_1=0.0,
    chi_2=0.0,
    network_snr=100.0,
    lambda_sigma=lambda_sigma_IMRPhenomD_33,
    prefix_injection_name = "at_flowmc-20240722113944_mean"
):

    injection_dict, duration = get_injection_dictionary_and_safe_duration_ripple(
        total_mass=total_mass,
        mass_ratio=mass_ratio,
        chi_1=chi_1,
        chi_2=chi_2,
        network_snr=network_snr,
        lambda_sigma=lambda_sigma
    )

    total_mass = injection_dict['total_mass']

    from utils.path_utils import get_path_to_repo_on_cluster
    path_to_repo_on_cluster = get_path_to_repo_on_cluster()

    path_H1 = path_to_repo_on_cluster + f"/data/analysis/bilby-inference/psd/AplusDesign_psd_total_mass_{total_mass}.txt"
    path_L1 = path_to_repo_on_cluster + f"/data/analysis/bilby-inference/psd/AplusDesign_psd_total_mass_{total_mass}.txt"
    path_V1 = path_to_repo_on_cluster + f"/data/analysis/bilby-inference/psd/avirgo_O5high_NEW_psd_total_mass_{total_mass}.txt"
    psd_dict = {'H1': path_H1, 'L1': path_L1, 'V1': path_V1}
    
    injection_folder = 'injection'
    if not os.path.exists(injection_folder):
        os.makedirs(injection_folder)
    injection_filename = f"ripple_{prefix_injection_name}_total_mass_{total_mass:.1f}_mass_ratio_{mass_ratio:.3f}_chi_1_{chi_1:.2f}_chi_2_{chi_2:.2f}_SNR_{network_snr:.1f}.inj"
    injection_file = os.path.join(injection_folder, injection_filename)
    maximum_frequency = 256

    with open(injection_file, 'w') as f:
        f.write("#" * 80 + "\n")
        f.write(f"## Injection for ripple. SNR = {network_snr:.1f} with H1,L1,V1 in O5\n")
        f.write("#" * 80 + "\n")
        f.write("injection-dict={\n")
        items = list(injection_dict.items())
        for i, (key, value) in enumerate(items):
            end_char = "\n" if i == len(items) - 1 else ",\n"
            f.write(f" '{key}': {value}{end_char}")
        f.write("}\n")
        f.write("#" * 80 + "\n")
        f.write(f"maximum-frequency = {float(maximum_frequency):.1f}\n")
        f.write("#" * 80 + "\n")
        f.write("## Effective maximum_frequency is 0.018/total_mass thanks to inspiral-only PSD \n")
        f.write("#" * 80 + "\n")
        f.write(f"psd_dict = {psd_dict}\n")
        f.write("#" * 80 + "\n")
        f.write("## Safely set duration \n")
        f.write("#" * 80 + "\n")
        f.write(f"duration = {duration:.0f}\n")
        f.write("#" * 80 + "\n")
    return None