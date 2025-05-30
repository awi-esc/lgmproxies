from pathlib import Path
import cloudpickle as cp
import numpy as np
import pymc as pm
import arviz as az
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
    def load(cls, model_path: str | Path, trace_path: str | Path):
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
        return cls(model, trace)

    def to_sst(self, delta_o18: np.ndarray, delta_o18_sw: np.ndarray, seed: int=345) -> np.ndarray:

        a = self.trace.posterior["a"].values.flatten()
        b = self.trace.posterior["b"].values.flatten()
        tau = self.trace.posterior["tau"].values.flatten()
        # d18oc_est = a + b * temp + (d18osw - 0.27) + N(0, tau)
        # -> temp = (delta_o18 - N(0, tau) - delta_o18_sw + 0.27) / b
        temp = (delta_o18 - delta_o18_sw + 0.27) / b[:, None] + a[:, None]
        # Add uncertainty from tau
        temp_err = np.random.normal(0, (tau/b)[:, None], size=temp.shape, seed=seed)

        return temp + temp_err