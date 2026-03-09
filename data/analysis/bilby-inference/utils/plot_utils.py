from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import os
import json
from tqdm import tqdm
import numpy as np
import corner
import bilby
from utils.parameter_conversion_utils import get_mass_1_and_mass_2_from_chirp_mass_and_mass_ratio, get_chi_eff_from_mass_1_and_mass_2_and_chi_1_and_chi_2, get_chi_hat_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2, get_symmetric_mass_ratio_from_mass_ratio


def save_corner_astro_parameters_and_phenom_coefficients_and_ppe_prior_vs_posterior(
    bilby_run_label,
    outdir='',
    plot_parameters = ['chirp_mass', 'mass_ratio', 'mass_1', 'mass_2', 'chi_1', 'chi_2', 'chi_hat','lambda_sigma_0','beta_ppe']
):

    astro_parameters = [
        'mass_1', 'mass_2', 'theta_jn', 'luminosity_distance', 'phase', 
        'geocent_time', 'chi_1', 'chi_2', 'mass_ratio', 'chirp_mass', 
        'total_mass', 'chi_eff', 'chi_hat', 'symmetric_mass_ratio','ra','dec'
    ]

    from utils.path_utils import get_path_to_bilby_runs_on_laptop
    path_to_bilby_runs_on_laptop = get_path_to_bilby_runs_on_laptop()

    base_directory = path_to_bilby_runs_on_laptop + f"/{bilby_run_label}/outdir/result"
    files = os.listdir(base_directory)
    json_files = [file for file in files if file.endswith(".json")]
    json_file_path = os.path.join(base_directory, json_files[0])

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    if data['meta_data']['command_line_args']['waveform_approximant'] == 'ripple_ppe':
        phenom_parameters = [f'lambda_sigma_{i}' for i in range(33)]
        ppe_parameters = ['beta_ppe']
    else:
        phenom_parameters = []
        ppe_parameters = []
        plot_parameters = [param for param in plot_parameters if not param.startswith('lambda_sigma_')]

    if data['meta_data']['command_line_args']['time_marginalization']:
        astro_parameters += ['time_jitter']

    injection_parameters = data['injection_parameters']
    injection_parameters['mass_1'] = injection_parameters.pop('mass-1')
    injection_parameters['chi_eff'] = get_chi_eff_from_mass_1_and_mass_2_and_chi_1_and_chi_2(injection_parameters['mass_1'],injection_parameters['mass_2'],injection_parameters['chi_1'], injection_parameters['chi_2'])
    injection_parameters['chi_hat'] = get_chi_hat_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2(injection_parameters['chirp_mass'], injection_parameters['mass_ratio'],injection_parameters['chi_1'],injection_parameters['chi_2'])
    injection_parameters['symmetric_mass_ratio'] = get_symmetric_mass_ratio_from_mass_ratio(injection_parameters['mass_ratio'])

    posterior_samples = {
        key: np.array(data['posterior']['content'][key])
        for key in (astro_parameters + phenom_parameters + ppe_parameters)
        if key != 'chi_hat'
    }
    posterior_samples['chi_hat'] = get_chi_hat_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2(posterior_samples['chirp_mass'], posterior_samples['mass_ratio'], posterior_samples['chi_1'], posterior_samples['chi_2'])
    n_draws_posterior = posterior_samples['chirp_mass'].shape[0]

    log_likelihood_ratio_samples = np.array(data['posterior']['content']['log_likelihood'])

    sample_index_of_maximum_likelihood = np.argmax(log_likelihood_ratio_samples)
    maximum_likelihood_point = {
        key: posterior_samples[key][sample_index_of_maximum_likelihood]
        for key in (astro_parameters + phenom_parameters + ppe_parameters)
    }
    
    priors = bilby.result.read_in_result(json_file_path).priors
    n_draws_prior = n_draws_posterior
    prior_samples = priors.sample(n_draws_prior)
    prior_samples['mass_1'], prior_samples['mass_2'] = get_mass_1_and_mass_2_from_chirp_mass_and_mass_ratio(prior_samples['chirp_mass'], prior_samples['mass_ratio'])
    prior_samples['chi_eff'] = get_chi_eff_from_mass_1_and_mass_2_and_chi_1_and_chi_2(prior_samples['mass_1'], prior_samples['mass_2'], prior_samples['chi_1'], prior_samples['chi_2'])
    prior_samples['chi_hat'] = get_chi_hat_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2(prior_samples['chirp_mass'], prior_samples['mass_ratio'], prior_samples['chi_1'], prior_samples['chi_2'])
    prior_samples['symmetric_mass_ratio'] = get_symmetric_mass_ratio_from_mass_ratio(prior_samples['mass_ratio'])
    prior_samples['total_mass'] = prior_samples['mass_1'] + prior_samples['mass_2']

    dim_plot = len(plot_parameters)
    colors = ['blue', 'red']
    labels = ['Prior', 'Posterior']
    dpi = 300
    fig, ax = plt.subplots(dim_plot, dim_plot, figsize=(25, 25), dpi=dpi)

    plot_posterior_data = np.array([posterior_samples[param] for param in plot_parameters]).T
    levels = [0.90] # contour enclosing 90% of the samples
    posterior_corner = corner.corner(plot_posterior_data, color=colors[1], fig=fig,
                no_fill_contours=True, 
                plot_contours=True, 
                levels=levels,
                plot_density=False, 
                plot_datapoints=True,
                hist_kwargs={'density': True, 'linewidth': 1})

    plot_maximum_likelihood_point = np.array([maximum_likelihood_point[param] for param in plot_parameters])

    plot_prior_data = np.array([prior_samples[param] for param in plot_parameters]).T
    prior_corner = corner.corner(plot_prior_data, color=colors[0], weights=np.ones(n_draws_prior) * n_draws_posterior / n_draws_prior, fig=fig,
                no_fill_contours=True, 
                plot_contours=True, 
                levels=levels,
                plot_density=False, 
                plot_datapoints=True,
                hist_kwargs={'density': True, 'linewidth': 1})

    # statistic, only parameters to plot
    plot_median_of_posterior = np.median(plot_posterior_data, axis=0)
    plot_lower_posterior = np.percentile(plot_posterior_data, 5, axis=0)
    plot_upper_posterior = np.percentile(plot_posterior_data, 95, axis=0)
    plot_median_of_prior = np.median(plot_prior_data, axis=0)

    xlim_min = np.percentile(plot_posterior_data, 0.000001, axis=0)
    xlim_max = np.percentile(plot_posterior_data, 99.99999, axis=0)

    # label, only parameters to plot
    axes = np.array(prior_corner.axes).reshape((dim_plot, dim_plot))
    for i in range(dim_plot):
        axes[-1, i].set_xlabel(plot_parameters[i], fontsize=18)
        axes[i, 0].set_ylabel(plot_parameters[i], fontsize=18)

    # use i index to go through plot, not the dict keys
    for i in tqdm(range(dim_plot), desc='diagonal plot'):
        ax = axes[i, i]
        ax.set_xlim(xlim_min[i], xlim_max[i])
        ax.axvline(plot_median_of_prior[i], color=colors[0], ls=':')
        ax.axvline(plot_median_of_posterior[i], color=colors[1], ls=':')
        ax.axvline(plot_maximum_likelihood_point[i], color='green', ls='-', label='maxL')
        ax.axvspan(plot_lower_posterior[i], plot_upper_posterior[i], color=colors[1], alpha=0.1)

        ci_text = f"({plot_lower_posterior[i]:.3f}, {plot_median_of_posterior[i]:.3f}, {plot_upper_posterior[i]:.3f})"
        label_text = "5th, 50th, 95th percentile:\n"
        ax.text(0.5, 1.05, label_text + ci_text, transform=ax.transAxes, fontsize=16, color=colors[1], ha='center')

        ax.text(0.5, 1.4, f"maxL: {plot_maximum_likelihood_point[i]:.3f}", transform=ax.transAxes, fontsize=16, color='green', ha='center')

        if plot_parameters[i] in injection_parameters.keys():
            ax.axvline(injection_parameters[plot_parameters[i]], color="k", ls='-', alpha=0.8)
            inj_value_text = f"Injected: {injection_parameters[plot_parameters[i]]:.3f}"
            ax.text(0.5, 1.6, inj_value_text, transform=ax.transAxes, fontsize=18, color="k", ha='center')
        else:
            ax.text(0.5, 1.6, "Not injected", transform=ax.transAxes, fontsize=18, color="k", ha='center')

    # use xi,yi indices to go through plot, not the dict keys
    for yi in tqdm(range(dim_plot), desc='pair plots'):
        for xi in range(yi):
            ax = axes[yi, xi]
            ax.set_xlim(xlim_min[xi], xlim_max[xi])
            ax.axvline(plot_median_of_prior[xi], color=colors[0], ls=':')
            ax.axvline(plot_median_of_posterior[xi], color=colors[1], ls=':')
            ax.axhline(plot_median_of_prior[yi], color=colors[0], ls=':')
            ax.axhline(plot_median_of_posterior[yi], color=colors[1], ls=':')

            ax.axvline(plot_maximum_likelihood_point[xi], color='green')
            ax.axhline(plot_maximum_likelihood_point[yi], color='green')

            if plot_parameters[yi] in injection_parameters.keys():
                ax.axhline(injection_parameters[plot_parameters[yi]], color="k", ls='-', lw=0.9)
            if plot_parameters[xi] in injection_parameters.keys():
                ax.axvline(injection_parameters[plot_parameters[xi]], color="k", ls='-', lw=0.9)
            if plot_parameters[yi] in injection_parameters.keys() and plot_parameters[xi] in injection_parameters.keys():
                ax.plot(injection_parameters[plot_parameters[xi]], injection_parameters[plot_parameters[yi]], marker='x', color="k", ls='-', alpha=1.0)

    for ax in fig.get_axes():
        ax.tick_params(axis='both', labelsize=18)

    handles = [mlines.Line2D([], [], color=colors[i], label=f"{labels[i]} (median dotted)", linewidth=10) for i in range(len(colors))]
    handles += [mlines.Line2D([], [], color="k", label="Injection", linewidth=10)]
    handles += [mlines.Line2D([], [], color="green", label="max likelihood", linewidth=10)]

    plt.legend(
        handles=handles,
        fontsize=35, frameon=False,
        bbox_to_anchor=(1, dim_plot), loc="upper right"
    )

    plt.subplots_adjust(top=0.9)
    plt.suptitle(f'Corner plot: run {bilby_run_label}', fontsize=30)

    save_path = os.path.join(outdir, f"corner_prior_vs_posterior_{bilby_run_label}.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)

    return None

def save_corner_astro_parameters_and_phenom_coefficients_and_ppe_posterior(
    bilby_run_label,
    outdir='',
    plot_parameters = ['chirp_mass', 'mass_ratio', 'mass_1', 'mass_2', 'chi_1', 'chi_2', 'chi_hat','lambda_sigma_0','beta_ppe']
):

    astro_parameters = [
        'mass_1', 'mass_2', 'theta_jn', 'luminosity_distance', 'phase', 
        'geocent_time', 'chi_1', 'chi_2', 'mass_ratio', 'chirp_mass', 
        'total_mass', 'chi_eff', 'chi_hat', 'symmetric_mass_ratio','ra','dec'
    ]

    from utils.path_utils import get_path_to_bilby_runs_on_laptop
    path_to_bilby_runs_on_laptop = get_path_to_bilby_runs_on_laptop()

    base_directory = path_to_bilby_runs_on_laptop + f"/{bilby_run_label}/outdir/result"
    files = os.listdir(base_directory)
    json_files = [file for file in files if file.endswith(".json")]
    json_file_path = os.path.join(base_directory, json_files[0])

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    if data['meta_data']['command_line_args']['waveform_approximant'] == 'ripple_ppe':
        phenom_parameters = [f'lambda_sigma_{i}' for i in range(33)]
        ppe_parameters = ['beta_ppe']
    else:
        phenom_parameters = []
        ppe_parameters = []
        plot_parameters = [param for param in plot_parameters if not param.startswith('lambda_sigma_')]

    if data['meta_data']['command_line_args']['time_marginalization']:
        astro_parameters += ['time_jitter']

    injection_parameters = data['injection_parameters']
    injection_parameters['mass_1'] = injection_parameters.pop('mass-1')
    injection_parameters['chi_eff'] = get_chi_eff_from_mass_1_and_mass_2_and_chi_1_and_chi_2(injection_parameters['mass_1'],injection_parameters['mass_2'],injection_parameters['chi_1'], injection_parameters['chi_2'])
    injection_parameters['chi_hat'] = get_chi_hat_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2(injection_parameters['chirp_mass'], injection_parameters['mass_ratio'],injection_parameters['chi_1'],injection_parameters['chi_2'])
    injection_parameters['symmetric_mass_ratio'] = get_symmetric_mass_ratio_from_mass_ratio(injection_parameters['mass_ratio'])

    posterior_samples = {
        key: np.array(data['posterior']['content'][key])
        for key in (astro_parameters + phenom_parameters + ppe_parameters)
        if key != 'chi_hat'
    }
    posterior_samples['chi_hat'] = get_chi_hat_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2(posterior_samples['chirp_mass'], posterior_samples['mass_ratio'], posterior_samples['chi_1'], posterior_samples['chi_2'])
    n_draws_posterior = posterior_samples['chirp_mass'].shape[0]

    log_likelihood_ratio_samples = np.array(data['posterior']['content']['log_likelihood'])

    sample_index_of_maximum_likelihood = np.argmax(log_likelihood_ratio_samples)
    maximum_likelihood_point = {
        key: posterior_samples[key][sample_index_of_maximum_likelihood]
        for key in (astro_parameters + phenom_parameters + ppe_parameters)
    }
    
    dim_plot = len(plot_parameters)
    colors = ['red']
    labels = ['Posterior']
    dpi = 300
    fig, ax = plt.subplots(dim_plot, dim_plot, figsize=(25, 25), dpi=dpi)

    plot_posterior_data = np.array([posterior_samples[param] for param in plot_parameters]).T
    levels = [0.90] # contour enclosing 90% of the samples
    posterior_corner = corner.corner(plot_posterior_data, color='red', fig=fig,
                no_fill_contours=True, 
                plot_contours=True, 
                levels=levels,
                plot_density=False, 
                plot_datapoints=True,
                hist_kwargs={'density': True, 'linewidth': 1})

    plot_maximum_likelihood_point = np.array([maximum_likelihood_point[param] for param in plot_parameters])

    # statistic, only parameters to plot
    plot_median_of_posterior = np.median(plot_posterior_data, axis=0)
    plot_lower_posterior = np.percentile(plot_posterior_data, 5, axis=0)
    plot_upper_posterior = np.percentile(plot_posterior_data, 95, axis=0)

    xlim_min = np.percentile(plot_posterior_data, 0.000001, axis=0)
    xlim_max = np.percentile(plot_posterior_data, 99.99999, axis=0)

    # label, only parameters to plot
    axes = np.array(posterior_corner.axes).reshape((dim_plot, dim_plot))
    for i in range(dim_plot):
        axes[-1, i].set_xlabel(plot_parameters[i], fontsize=18)
        axes[i, 0].set_ylabel(plot_parameters[i], fontsize=18)

    # use i index to go through plot, not the dict keys
    for i in tqdm(range(dim_plot), desc='diagonal plot'):
        ax = axes[i, i]
        ax.set_xlim(xlim_min[i], xlim_max[i])
        ax.axvline(plot_median_of_posterior[i], color='red', ls=':')
        ax.axvline(plot_maximum_likelihood_point[i], color='green', ls='-', label='maxL')
        ax.axvspan(plot_lower_posterior[i], plot_upper_posterior[i], color='red', alpha=0.1)

        ci_text = f"({plot_lower_posterior[i]:.4e}, {plot_median_of_posterior[i]:.4e}, {plot_upper_posterior[i]:.4e})"
        label_text = "5th, 50th, 95th percentile:\n"
        ax.text(0.5, 1.05, label_text + ci_text, transform=ax.transAxes, fontsize=16, color='red', ha='center')

        ax.text(0.5, 1.4, f"maxL: {plot_maximum_likelihood_point[i]:.4e}", transform=ax.transAxes, fontsize=16, color='green', ha='center')

        if plot_parameters[i] in injection_parameters.keys():
            ax.axvline(injection_parameters[plot_parameters[i]], color="k", ls='-', alpha=0.8)
            inj_value_text = f"Injected: {injection_parameters[plot_parameters[i]]:.4e}"
            ax.text(0.5, 1.6, inj_value_text, transform=ax.transAxes, fontsize=18, color="k", ha='center')
        else:
            ax.text(0.5, 1.6, "Not injected", transform=ax.transAxes, fontsize=18, color="k", ha='center')

    # use xi,yi indices to go through plot, not the dict keys
    for yi in tqdm(range(dim_plot), desc='pair plots'):
        for xi in range(yi):
            ax = axes[yi, xi]
            ax.set_xlim(xlim_min[xi], xlim_max[xi])
            ax.axvline(plot_median_of_posterior[xi], color='red', ls=':')
            ax.axhline(plot_median_of_posterior[yi], color='red', ls=':')

            ax.axvline(plot_maximum_likelihood_point[xi], color='green')
            ax.axhline(plot_maximum_likelihood_point[yi], color='green')

            if plot_parameters[yi] in injection_parameters.keys():
                ax.axhline(injection_parameters[plot_parameters[yi]], color="k", ls='-', lw=0.9)
            if plot_parameters[xi] in injection_parameters.keys():
                ax.axvline(injection_parameters[plot_parameters[xi]], color="k", ls='-', lw=0.9)
            if plot_parameters[yi] in injection_parameters.keys() and plot_parameters[xi] in injection_parameters.keys():
                ax.plot(injection_parameters[plot_parameters[xi]], injection_parameters[plot_parameters[yi]], marker='x', color="k", ls='-', alpha=1.0)

    for ax in fig.get_axes():
        ax.tick_params(axis='both', labelsize=18)

    handles = [mlines.Line2D([], [], color='red', label=f"{labels[i]} (median dotted)", linewidth=10) for i in range(len(colors))]
    handles += [mlines.Line2D([], [], color="k", label="Injection", linewidth=10)]
    handles += [mlines.Line2D([], [], color="green", label="max likelihood", linewidth=10)]

    plt.legend(
        handles=handles,
        fontsize=35, frameon=False,
        bbox_to_anchor=(1, dim_plot), loc="upper right"
    )

    plt.subplots_adjust(top=0.9)
    plt.suptitle(f'Corner plot: run {bilby_run_label}', fontsize=30)

    save_path = os.path.join(outdir, f"corner_posterior_{bilby_run_label}.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)

    return None