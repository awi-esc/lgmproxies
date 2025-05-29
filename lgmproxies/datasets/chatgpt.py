"""Simpe functions from Chat GPT

https://chatgpt.com/share/682f9b2c-ab58-8008-9a48-dbffbbdbf2e9

for a first round
"""
import pandas as pd
import numpy as np

def uk37_to_sst(uk37):
    """Convert UK'37 to sea surface temperature using Müller et al. (1998)."""
    return (uk37 - 0.044) / 0.033  # SST in °C


def uk37_error(uk37):
    """Estimate standard error for UK'37 SST reconstructions."""
    return np.where(uk37 >= 0.97,  # approaching saturation
        2.0,
        1.5  # °C
    )

def tex86_to_sst(tex86):
    """Convert TEX86 to sea surface temperature (SST) using Kim et al. (2010)."""
    return 68.4 * tex86 - 38.6  # SST in °C

def tex86_error(tex86):
    """Return standard error for TEX86-derived SST (Kim et al. 2010)."""
    return 2.5  # °C, can be regionally adjusted

def tex86_to_sst_monte_carlo(tex86, lat, n_samples=1000, seed=None):
    """
    Monte Carlo simulation of SST from TEX86 using a simple latitude-dependent calibration.

    Parameters:
        tex86: array-like of TEX86 proxy values
        lat: array-like of latitudes (same length as tex86)
        n_samples: number of Monte Carlo samples
        seed: random seed for reproducibility

    Returns:
        df_results: DataFrame with SST mean and std for each input
        sst_cov: Covariance matrix of SST estimates across all points
    """
    tex86 = np.asarray(tex86)
    lat = np.asarray(lat)

    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    # Simple latitude-dependent slope (more refined models use splines or MCMC)
    slope = np.where(np.abs(lat) < 30, 50, 55)  # Tropics vs extratropics
    intercept = -15  # Simple baseline intercept

    # Uncertainty assumptions (can be refined)
    slope_std = 2.0
    intercept_std = 1.5
    tex86_std = 0.02  # assumed measurement error

    n = len(tex86)
    sst_samples = np.empty((n_samples, n))

    for i in range(n_samples):
        slope_i = slope + rng.normal(0, slope_std, size=n)
        intercept_i = intercept + rng.normal(0, intercept_std)
        tex86_i = tex86 + rng.normal(0, tex86_std, size=n)
        sst_samples[i] = slope_i * tex86_i + intercept_i

    return sst_samples
    # sst_mean = sst_samples.mean(axis=0)
    # sst_std = sst_samples.std(axis=0)
    # sst_cov = np.cov(sst_samples.T)

    # df_results = pd.DataFrame({
    #     'tex86': tex86,
    #     'lat': lat,
    #     'sst_mean': sst_mean,
    #     'sst_std': sst_std
    # })

    # return df_results, sst_cov


def delta18o_to_temp(delta18o_c, delta18o_sw=0.0):
    """
    Convert δ18O of calcite (‰ VPDB) to temperature (°C).
    delta18o_sw: seawater δ18O (‰ VSMOW, converted to VPDB by -0.27‰).
    """
    delta = delta18o_c - (delta18o_sw - 0.27)  # match standards
    return 16.9 - 4.38 * delta + 0.1 * delta**2  # °C

def delta18o_error(delta18o_c=None):
    """Estimate uncertainty in δ18O paleotemperature."""
    return 1.5  # °C typical if δ18O_sw is estimated reasonably


def mgca_to_temp(mgca):
    """Convert Mg/Ca ratio (mmol/mol) to temperature using Anand et al. (2003)."""
    return (np.log(mgca / 0.38)) / 0.09  # SST in °C


def mgca_error(mgca=None):
    """Estimate uncertainty in Mg/Ca-derived SST."""
    return 1.5  # °C, typical combined error

