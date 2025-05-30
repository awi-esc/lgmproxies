import os
from pathlib import Path
import lgmproxies

def get_xdg_cache_dir() -> Path:
    # Check if XDG_CACHE_HOME is set
    xdg_cache_home = os.environ.get('XDG_CACHE_HOME')

    # If XDG_CACHE_HOME is not set, use the default cache directory
    if xdg_cache_home is None:
        xdg_cache_home = os.path.expanduser('~/.cache')

    return Path(xdg_cache_home)

CACHE = get_xdg_cache_dir() / 'lgmproxies'
PACKAGE_DIR = Path(lgmproxies.__file__).parent

def create_cache_dir():
    # Create the cache directory if it doesn't exist
    CACHE.mkdir(parents=True, exist_ok=True)

def get_datapath(name: str | Path="") -> Path:
    return CACHE / Path(name)

def get_figpath(name: str | Path="") -> Path:
    return Path("figures")/ name

def get_repo(name: str | Path="") -> Path:
    return Path(PACKAGE_DIR) / name