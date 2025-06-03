from pathlib import Path
import pandas as pd
import cloudpickle as cp
import numpy as np
import pymc as pm
import arviz as az
from scipy.interpolate import NearestNDInterpolator
from lgmproxies.logs import logger
from lgmproxies.datasets.manager import get_repo_path

TIERNEY_REPOS = [
    "jesstierney/lgmDA",
    "jesstierney/BAYSPLINE",
    "jesstierney/BAYMAG",
    "jesstierney/BAYSPAR",
    "brews/baysparpy", # python port of jesstierney/BAYSPAR
    # "brews/bayfox", # foram calibration: pypi
    # "brews/erebusfall", # d18O correction adapted from Tierney al 2017 https://doi.org/10.1130/G39457.1: pypi
    "brews/d18oc_sst", # d18O correction from Malevich et al 2019 https://doi.org/10.1029/2019PA003576
    ]


class DeltaO18:
    """
    Class for handling delta O18 data and its conversion to sea surface temperature (SST).
    """
    def __init__(self, model: pm.Model, trace: az.InferenceData):
        self.model = model
        self.trace = trace

    @classmethod
    def load(cls, model_path: str | Path, trace_path: str | Path, **kwargs) -> "DeltaO18":
        """
        Load a DeltaO18 model and its trace from specified paths.

        Args:
            model_path (str | Path): Path to the PyMC model file.
            trace_path (str | Path): Path to the ArviZ trace file.

        Returns:
            DeltaO18: An instance of the DeltaO18 class.
        """
        model = cp.load(open(model_path, "rb"))
        trace = az.from_netcdf(trace_path)
        return cls(model, trace, **kwargs)

    def to_sst(self, delta_o18: np.ndarray, delta_o18_sw: np.ndarray, seed: int=345, rng=None) -> np.ndarray:
        if rng is None:
            rng = np.random.default_rng(seed)
        a = self.trace.posterior["a"].values.flatten()
        b = self.trace.posterior["b"].values.flatten()
        tau = self.trace.posterior["tau"].values.flatten()
        # d18oc_est = a + b * temp + (d18osw - 0.27) + N(0, tau)
        # -> temp = (delta_o18 - N(0, tau) - delta_o18_sw + 0.27) / b
        temp = (delta_o18 - a[:, None] - delta_o18_sw + 0.27) / b[:, None]
        # Add uncertainty from tau
        temp_err = rng.normal(0, (tau/np.abs(b))[:, None], size=temp.shape)

        return temp + temp_err


CATEGORIES = ["bulloides", "ruber", "incompta", "pachy", "sacculifer"]

class DeltaO18Hierarchical(DeltaO18):
    def __init__(self, model: pm.Model, trace: az.InferenceData, categories: list[str] = CATEGORIES):
        """
        Initialize the DeltaO18Hierarchical class.

        Args:
            model (pm.Model): The PyMC model.
            trace (az.InferenceData): The ArviZ trace data.
            categories (list[str]): List of species categories.
        """
        super().__init__(model, trace)
        if categories is None:
            categories = CATEGORIES
        self.categories = categories

    def to_sst(self, delta_o18: np.ndarray,
               species: np.ndarray, delta_o18_sw: np.ndarray,
               seed: int = 345, rng=None) -> np.ndarray:
        """
        delta_o18: 1D array of delta O-18 values for each sample
        species: 1D array of species names corresponding to each delta O-18 value
        supported names are: "ruber", "bulloides", "pachy", "sacculifer", "incompta"

        The dataset was originally used in Malevitch et al. 2019 with names:
foramtype
G. bulloides     291 -> 0 - "bulloides"
G. ruber         489 -> 1 - "ruber"
N. incompta       90 -> 2 - "incompta"
N. pachyderma    273 -> 3 - "pachy"
T. sacculifer    243 -> 4 - "sacculifer"
Name: count, dtype: int64
"""
        if not species.dtype.kind == "i":
            species = np.asarray([self.categories.index(s) for s in species])
        if rng is None:
            rng = np.random.default_rng(seed)
        post = az.extract(self.trace.posterior)
        a = post["a"].values
        assert a.ndim == 2, f"Expected a to be 2D (samples, species). Got {a.ndim}D: {a.shape}"
        b = post["b"].values
        tau = post["tau"].values
        # d18oc_est = a + b * temp + (d18osw - 0.27) + N(0, tau)
        # -> temp = (delta_o18 - N(0, tau) - delta_o18_sw + 0.27) / b
        temp = (delta_o18 - a[:, species] - delta_o18_sw + 0.27) / b[:, species]
        # Add uncertainty from tau
        temp_err = rng.normal(0, (tau/np.abs(b))[:, species], size=temp.shape)

        return temp + temp_err





class DeloSWMalevitch:
    def __init__(self):
        repo = get_repo_path("brews/d18oc_sst")
        self.coretops_raw = pd.read_csv(repo/"data/parsed/coretops.csv")
        self.coretops_grid = pd.read_csv(repo/"data/parsed/coretops_grid.csv")

        # Combine latitude and longitude into a single array of coordinates
        # Extract latitude, longitude, and d18osw values
        data = self.coretops_grid
        latitudes = data['gridlat'].values
        longitudes = data['gridlon'].values
        d18osw_values = data['d18osw'].values
        points = np.column_stack((latitudes, longitudes))

        # Create the nearest neighbor interpolator
        self.interpolator = NearestNDInterpolator(points, d18osw_values)

    def interpolate(self, longitude: float, latitude: float) -> float:
        # Example: Predict d18osw value at a new point
        new_point = np.array([latitude, longitude]).T  # Replace with actual values
        return self.interpolator(new_point)
