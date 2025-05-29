from pathlib import Path
from lgmproxies.logs import logger
from lgmproxies.datasets.manager import get_repo_path

TIERNEY_REPOS = [
    "jesstierney/BAYSPLINE",
    "jesstierney/BAYMAG",
    "jesstierney/BAYSPAR",
    "brews/baysparpy", # python port of jesstierney/BAYSPAR
    # "brews/bayfox", # foram calibration: pypi
    # "brews/erebusfall", # d18O correction adapted from Tierney al 2017 https://doi.org/10.1130/G39457.1: pypi
    "brews/d18oc_sst", # d18O correction from Malevich et al 2019 https://doi.org/10.1029/2019PA003576
    ]


