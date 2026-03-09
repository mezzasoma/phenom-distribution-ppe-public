from utils.constants import lambda_sigma_IMRPhenomD_33
from utils.prior_utils import (save_ppe_and_delta_prior_file_ripple,
                               save_ppe_and_flowmc_gaussian_prior_file_ripple,
                               save_no_ppe_and_delta_prior_file_ripple)

mass_ratio = 0.43419265791678147
total_masses = [20.0, 60.0]
ppe_PN_orders = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 3.5]
beta_ppe_prior_bounds = {
    20.0: {
        -1.5: (-3.00e-7,  4.67e-7),
        -1.0: (-3.41e-6,  7.07e-6),
        -0.5: (-5.69e-5,  1.739e-4),
         0.0: (-3.27e-3,  4.55e-3),
         0.5: (-1.83e-2,  1.17e-2),
         1.0: (-1.35e-1,  7.01e-2),
         1.5: (-1.89e+0,  6.20e-1),
         2.0: (-1.140e+1, 7.13e+0),
         3.0: (-8.46e+1,  1.285e+2),
         3.5: (-3.96e+2,  5.33e+2),
    },
    60.0: {
        -1.5: (-4.54e-6,  9.46e-6),
        -1.0: (-5.13e-5,  1.324e-4),
        -0.5: (-6.38e-4,  1.078e-3),
         0.0: (-6.01e-3,  5.70e-3),
         0.5: (-3.82e-2,  2.35e-2),
         1.0: (-2.04e-1,  1.08e-1),
         1.5: (-1.87e+0,  6.43e-1),
         2.0: (-2.93e+1,  1.14e+1),
         3.0: (-3.66e+2,  4.36e+2),
         3.5: (-7.39e+2,  7.93e+2),
    },
}

for total_mass in total_masses:
    for ppe_PN_order in ppe_PN_orders:
        save_ppe_and_delta_prior_file_ripple(
            total_mass=total_mass,
            mass_ratio=mass_ratio,
            ppe_PN_order = ppe_PN_order,
            beta_ppe_prior_min=beta_ppe_prior_bounds[total_mass][ppe_PN_order][0],
            beta_ppe_prior_max=beta_ppe_prior_bounds[total_mass][ppe_PN_order][1],
            lambda_sigma=lambda_sigma_IMRPhenomD_33,
            prefix_prior_name = "delta_at_IMRPhenomD"
        )

        # save_ppe_and_flowmc_gaussian_prior_file_ripple(
        #     total_mass=total_mass,
        #     mass_ratio=mass_ratio,
        #     ppe_PN_order = ppe_PN_order,
        #     beta_ppe_prior_min=beta_ppe_prior_bounds[total_mass][ppe_PN_order][0],
        #     beta_ppe_prior_max=beta_ppe_prior_bounds[total_mass][ppe_PN_order][1],
        #     flowmc_run_label = "flowmc-20240722113944"
        # )

        save_no_ppe_and_delta_prior_file_ripple(
            total_mass=total_mass,
            mass_ratio=mass_ratio,
            lambda_sigma=lambda_sigma_IMRPhenomD_33,
            prefix_prior_name = "delta_at_IMRPhenomD"
        )