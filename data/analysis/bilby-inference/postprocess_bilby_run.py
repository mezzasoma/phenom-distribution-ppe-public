from utils.path_utils import create_and_set_outdir
from utils.plot_utils import (
    save_corner_astro_parameters_and_phenom_coefficients_and_ppe_prior_vs_posterior,
    save_corner_astro_parameters_and_phenom_coefficients_and_ppe_posterior
)

outdir = create_and_set_outdir("postprocess-bilby-run")

bilby_run_label = '20251012052238' # USER INPUT: replace with run that you want to inspect
plot_parameters = [
    'chirp_mass',
    'mass_ratio',
    'chi_hat',
    'beta_ppe',
    'lambda_sigma_0',
    'lambda_sigma_1',
    'ra',
    'dec',
    'luminosity_distance'
]

save_corner_astro_parameters_and_phenom_coefficients_and_ppe_prior_vs_posterior(
    bilby_run_label,
    outdir,
    plot_parameters
)
save_corner_astro_parameters_and_phenom_coefficients_and_ppe_posterior(
    bilby_run_label,
    outdir,
    plot_parameters
)
