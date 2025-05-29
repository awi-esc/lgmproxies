from pathlib import Path
import urllib
import subprocess as sp
import urllib.parse
from lgmproxies.logs import logger
from lgmproxies.config import get_datapath

TIERNEY_REPOS = ["jesstierney/BAYSPLINE", "jesstierney/BAYMAG", "jesstierney/BAYSPAR", "brews/baysparpy", "brews/d18oc_sst", "brews/bayfox"]
