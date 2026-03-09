from utils.constants import lambda_sigma_IMRPhenomD_33
import os

def get_IMRPhenomD_prior(total_mass, mass_ratio):

    chirp_mass = total_mass * mass_ratio**(3.0 / 5.0) * (1.0 + mass_ratio)**(-6.0 / 5.0)
    mass_ratio_min = 0.05
    print(
        "For total_mass = 20 MSUN, the default chirp mass prior half-width is 14 percent of the injected chirp mass value. "
        "For total_mass = 60 MSUN, it is 20 percent. "
        "These bounds should be safe for SNR~50-330. "
        "Manually edit the minimum and maximum chirp mass prior if the tails of the posterior distribution are cut by the prior. "
    )
    if total_mass == 20.0:
        fractional_half_width_for_chirp_mass = 0.14
    elif total_mass == 60.0:
        fractional_half_width_for_chirp_mass = 0.20
    else:
        fractional_half_width_for_chirp_mass = 0.20

    chirp_mass_min = chirp_mass * (1.0 - fractional_half_width_for_chirp_mass)
    chirp_mass_max = chirp_mass * (1.0 + fractional_half_width_for_chirp_mass)
    luminosity_distance_min = 5.0
    luminosity_distance_max = 1200.0

    print(
        f"The default prior for the luminosity distance spans the interval [{luminosity_distance_min:.1f},{luminosity_distance_max:.1f}] Mpc. "
        "This should work for a BBH with total mass 20-60 MSUN at SNRs~50-330. "
        "Manually restrict the prior interval to improve sampling resolution if needed."
    )
    print("")

    prior_content = f"""
chirp_mass = bilby.gw.prior.UniformInComponentsChirpMass(name='chirp_mass', minimum={chirp_mass_min:.2f}, maximum={chirp_mass_max:.2f}, unit='$M_{{\\odot}}$')
mass_ratio = bilby.gw.prior.UniformInComponentsMassRatio(name='mass_ratio', minimum={mass_ratio_min:.3f}, maximum=1.0)
chi_1 = bilby.core.prior.Uniform(name='chi_1', minimum=-0.999, maximum=0.999)
chi_2 = bilby.core.prior.Uniform(name='chi_2', minimum=-0.999, maximum=0.999)
luminosity_distance = bilby.gw.prior.UniformSourceFrame(name='luminosity_distance', minimum={luminosity_distance_min:.1f}, maximum={luminosity_distance_max:.1f})
dec = Cosine(name='dec')
ra = Uniform(name='ra', minimum=0, maximum=2 * np.pi, boundary='periodic')
theta_jn = Sine(name='theta_jn')
psi = Uniform(name='psi', minimum=0, maximum=np.pi, boundary='periodic')
phase = Uniform(name='phase', minimum=0, maximum=2 * np.pi, boundary='periodic')
"""
    return prior_content.strip()

def save_no_ppe_and_delta_prior_file_ripple(
    total_mass=20.0,
    mass_ratio=0.4,
    lambda_sigma=lambda_sigma_IMRPhenomD_33,
    prefix_prior_name = "delta_at_IMRPhenomD"
):
    
    IMRPhenomD_prior = get_IMRPhenomD_prior(total_mass, mass_ratio)

    no_ppe_prior_content = f"""
beta_ppe = DeltaFunction(peak=0.0, name='beta_ppe')
b_ppe = DeltaFunction(peak=+99.0, name='b_ppe')
"""

    ppe_prior = no_ppe_prior_content.strip()
    lambda_sigma_prior = "\n".join(
        [f"lambda_sigma_{i} = DeltaFunction(peak={value:.20e}, name='lambda_sigma_{i}')" 
            for i, value in enumerate(lambda_sigma)]
    )

    prior = IMRPhenomD_prior + "\n" + ppe_prior + "\n" + lambda_sigma_prior

    prior_folder = 'prior'
    if not os.path.exists(prior_folder):
        os.makedirs(prior_folder)

    prior_filename = f"ripple_{prefix_prior_name}_total_mass_{total_mass:.1f}_mass_ratio_{mass_ratio:.3f}_no_ppe.prior"
    prior_file = os.path.join(prior_folder, prior_filename)
    with open(prior_file, 'w') as file:
        file.write(prior)
    return None

def get_ppe_prior(ppe_PN_order=-1, beta_ppe_prior_min=-1.0e-4, beta_ppe_prior_max=+1.0e-4):

    b_ppe = -5 + 2 * ppe_PN_order
    prior_content = f"""
beta_ppe = bilby.core.prior.Uniform(name='beta_ppe', minimum={beta_ppe_prior_min:.2e}, maximum={beta_ppe_prior_max:.2e})
b_ppe = DeltaFunction(peak={b_ppe:.1f}, name='b_ppe')
"""
    return prior_content.strip()

def save_ppe_and_delta_prior_file_ripple(
    total_mass=20.0,
    mass_ratio=0.4,
    ppe_PN_order = -1,
    beta_ppe_prior_min=-1.0e-4, 
    beta_ppe_prior_max=+1.0e-4,
    lambda_sigma=lambda_sigma_IMRPhenomD_33,
    prefix_prior_name = "delta_at_IMRPhenomD"
):
    
    IMRPhenomD_prior = get_IMRPhenomD_prior(total_mass, mass_ratio)
    ppe_prior = get_ppe_prior(ppe_PN_order, beta_ppe_prior_min, beta_ppe_prior_max)
    lambda_sigma_prior = "\n".join(
        [f"lambda_sigma_{i} = DeltaFunction(peak={value:.20e}, name='lambda_sigma_{i}')" 
            for i, value in enumerate(lambda_sigma)]
    )

    prior = IMRPhenomD_prior + "\n" + ppe_prior + "\n" + lambda_sigma_prior

    prior_folder = 'prior'
    if not os.path.exists(prior_folder):
        os.makedirs(prior_folder)

    prior_filename = f"ripple_{prefix_prior_name}_total_mass_{total_mass:.1f}_mass_ratio_{mass_ratio:.3f}_ppe_{ppe_PN_order}PN.prior"
    prior_file = os.path.join(prior_folder, prior_filename)
    with open(prior_file, 'w') as file:
        file.write(prior)
    return None

def save_ppe_and_flowmc_gaussian_prior_file_ripple(
    total_mass=20.0,
    mass_ratio=0.4,
    ppe_PN_order=-1,
    beta_ppe_prior_min=-1.0e-4, 
    beta_ppe_prior_max=+1.0e-4,
    flowmc_run_label = "flowmc-20240722113944"
):
    
    IMRPhenomD_prior = get_IMRPhenomD_prior(total_mass, mass_ratio)
    ppe_prior = get_ppe_prior(ppe_PN_order, beta_ppe_prior_min, beta_ppe_prior_max)

    from utils.path_utils import get_path_to_flowmc_gaussian_prior_on_laptop
    path_to_flowmc_gaussian_prior_on_laptop = get_path_to_flowmc_gaussian_prior_on_laptop()

    gaussian_appendix = os.path.join(path_to_flowmc_gaussian_prior_on_laptop, f'{flowmc_run_label}_gaussian_prior_appendix.prior')
    with open(gaussian_appendix, 'r') as appendix_file:
        gaussian_prior = appendix_file.read().strip()

    prior = IMRPhenomD_prior + "\n" + ppe_prior + "\n" + gaussian_prior

    prior_folder = 'prior'
    if not os.path.exists(prior_folder):
        os.makedirs(prior_folder)

    prior_filename = f"ripple_{flowmc_run_label}_gaussian_total_mass_{total_mass:.1f}_mass_ratio_{mass_ratio:.3f}_ppe_{ppe_PN_order}PN.prior"
    prior_file = os.path.join(prior_folder, prior_filename)
    with open(prior_file, 'w') as file:
        file.write(prior)
    return None