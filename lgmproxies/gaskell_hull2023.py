"""ChatGPT-enabled client for Gaskell et al webtool
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import hashlib
import pickle
from lgmproxies.datasets.manager import get_datapath

calibration_options = [
    "bayfox_pooled",
    "bayfox_ruber",
    "bayfox_bulloides",
    "bayfox_globigerina",
    "kim_oneil",
    "epstein",
    "grossman",
    "bemis",
    "marchitto",
    "anand",
    "elderfield",
    "gaskell"
]


timescale_options = [
    "GTS2020", "GTS2012", "LR04", "LR09", "CENOGRID", "Probstack"
]

ice_options = [
    "none", "rohling1", "rohling2", "fairbanks", "waelbroeck"
]

spatial_options = [
    "none", "gaskell_poly", "legrande_mixed", "legrande_0m", "legrande_50m",
    "legrande_100m", "legrande_200m", "legrande_500m", "legrande_1000m",
    "legrande_1500m", "legrande_2000m", "legrande_3000m", "legrande_4000m",
    "legrande_5000m", "tierney_lateholocene", "tierney_lastglaciermaximum", "zachos",
    "hollis", "gaskell_lat"
]

benthic_options = [
    "none", "fixed",
    "cramer1", "cramer2", "cramer3",
    "cramer1s", "cramer2s", "cramer3s",
    # "cramer_s4", "cramer_s5", "cramer_s6",
    # "cramer_s4_smooth", "cramer_s5_smooth", "cramer_s6_smooth",
    # "meckler", "miller", "rohling_cenogrid", "rohling_lr04"
    "meckler",
    "miller",
    "rohling1",  # Rohling et al. 2021 CENOGRID (0-40 Ma, SL-d18O)
    "rohling2", #  Rohling et al. 2021 LR04 (0-5.3 Ma, SL-d18O)
]

co3_options = [
    "none", "sosd"
]

cachefile = get_datapath("gaskell_hull2023_cache.pkl")

def hash_dataframe(df):
    """
    Return a hash of a DataFrame's content for use as a cache key.
    """
    df_bytes = pd.util.hash_pandas_object(df, index=True).values.tobytes()
    return hashlib.sha256(df_bytes).hexdigest()

def cached(func):
    """
    Decorator to cache the results of the function.
    """
    if cachefile.exists():
        with open(cachefile, 'rb') as f:
            cache = pickle.load(f)
    else:
        cache = {}

    def wrapper(df_input, *args, **kwargs):
        df_hash = hash_dataframe(df_input)
        key = (df_hash, args, frozenset(kwargs.items()))
        if key not in cache:
            result = func(df_input.copy(), *args, **kwargs)
            cache[key] = result
            with open(cachefile, 'wb') as f:
                pickle.dump(cache, f)
        return cache[key]

    return wrapper

@cached
def convert_d18o_df(
    df_input,
    calibration='bayfox_pooled',
    timescale='GTS2020',
    ice='rohling1',
    latlong='none',
    spatial='gaskell_poly',
    benthic='rohling1',
    co3='none'
):
    """
    Submit a d18O DataFrame to the Yale d18O converter and return the converted DataFrame.

    Parameters
    ----------
    df_input : pd.DataFrame
        Must contain columns: d18O, age, lat, long
    calibration, timescale, ice, latlong, spatial, benthic, co3 : str
        Options passed to the converter form

    Returns
    -------
    pd.DataFrame
        DataFrame with original and computed temperature estimates
    """

    # Ensure correct columns
    required_cols = ['d18O', 'age', 'lat', 'long']
    for col in required_cols:
        if col not in df_input.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert to CSV string
    csv_buffer = StringIO()
    df_input.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    files = {
        'filename': ('input.csv', csv_buffer, 'text/csv'),
    }

    data = {
        'calibration': calibration,
        'timescale': timescale,
        'ice': ice,
        'latlong': latlong,
        'spatial': spatial,
        'benthic': benthic,
        'co3': co3,
    }

    # validate options
    if calibration not in calibration_options:
        raise ValueError(f"Invalid calibration option: {calibration}. Must be one of {calibration_options}")
    if timescale not in timescale_options:
        raise ValueError(f"Invalid timescale option: {timescale}. Must be one of {timescale_options}")
    if ice not in ice_options:
        raise ValueError(f"Invalid ice option: {ice}. Must be one of {ice_options}")
    if latlong not in ['none', 'latlong']:
        raise ValueError(f"Invalid latlong option: {latlong}. Must be 'none' or 'latlong'")
    if spatial not in spatial_options:
        raise ValueError(f"Invalid spatial option: {spatial}. Must be one of {spatial_options}")
    if benthic not in benthic_options:
        raise ValueError(f"Invalid benthic option: {benthic}. Must be one of {benthic_options}")
    if co3 not in co3_options:
        raise ValueError(f"Invalid co3 option: {co3}. Must be one of {co3_options}")

    url = "https://research.peabody.yale.edu/d180/proxy.php"
    response = requests.post(url, files=files, data=data)
    response.raise_for_status()

    return read_html_results(response.text)


# Load the HTML file

def read_html_results(html_content: str) -> pd.DataFrame:
    """
    Read the HTML file and extract the first table as a DataFrame.

    Parameters:
        html_file_path (str): Path to the HTML file.

    Returns:
        pd.DataFrame: DataFrame containing the first table found in the HTML.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract tables from the HTML
    tables = soup.find_all("table")

    # Convert each table to a DataFrame and save the first one to CSV
    if not tables:
        raise ValueError("No tables found in the HTML file.")

    df = pd.read_html(StringIO(str(tables[0])))[0]
    return df