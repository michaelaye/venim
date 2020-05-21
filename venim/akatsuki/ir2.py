from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
from urlpath import URL

from ..config import config
from ..pathmanager import PathManager

storage_root = Path(config["venim_path"]).expanduser()

level_urls = {
    "raw": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_0001/data/"),
    "calibrated": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_1001/data/l2b/"),
    "geom": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_2001/geometry/"),
}


def get_datestr_from_filename(filename):
    return filename.split("_")[1]


def get_rev_filelist(rev, level="calibrated"):
    level = [i for i in level_urls.keys() if level in i][0]
    results = pd.read_html(str(level_urls[level] / rev), skiprows=2)
    df = results[0]
    df = df.drop("Unnamed: 0", axis=1).dropna(how="all")
    df.columns = ["filename", "time", "size", "unnamed"]
    df = df[["filename", "time", "size"]]
    df["datestr"] = df.filename.map(lambda x: x.split("_")[1])
    df["timestr"] = df.filename.map(lambda x: x.split("_")[2])
    df["datetime"] = pd.to_datetime(df.datestr + " " + df.timestr)
    return df


def download_rev(rev, level="calibrated", force=False):
    """Download data for a given revolution (i.e. orbit)

    Will check for existence of files and not download again.
    Existing files can be overwritten using force=True as a parameter.

    Parameters
    ----------
    rev : str
        Revolution ID, i.e. "r0025"
    level : {"raw", "calibrated", "geom}, optional.
        String identifying the data level wanted. Default: "calibrated".
    force : bool, optional
        Overwrite existing data.
    """
    # allow 'calib' or 'geo' as level name
    # if the key in level_urls starts with given 'level' it will be selected
    level = [key for key in level_urls.keys() if key.startswith(level)][0]
    dirlist = get_rev_filelist(rev)
    storage_dir = Path(config["venim_path"]).expanduser()
    storage_dir.mkdir(exist_ok=True, parents=True)
    for fname in dirlist.filename:
        print(f"Downloading {fname}")
        url = level_urls[level] / rev / fname
        print(url)
        urlretrieve(str(url), storage_dir, use_tqdm=False)


class IR2PathManager(PathManager):
    def __init__(self):
        super().__init__("akatsuki", "ir2")

    @property
    def raw_savedir(self):
        return self.instr_savedir / "raw"

    @property
    def calibrated_savedir(self):
        return self.instr_savedir / "calibrated"

    @property
    def geometry_savedir(self):
        return self.instr_savedir / "geometry"
