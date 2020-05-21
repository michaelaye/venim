from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
import pvl
import requests
from tqdm.auto import tqdm
from urlpath import URL

from ..config import config
from ..pathmanager import PathManager

storage_root = Path(config["venim_path"]).expanduser()
storage_root.mkdir(exist_ok=True, parents=True)

level_urls = {
    "raw": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_0001/data/"),
    "calibrated": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_1001/data/l2b/"),
    "geom": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_2001/geometry/"),
}


def get_rev_filelist(rev, level="calibrated"):
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
    dirlist = get_rev_filelist(rev)
    storage_dir = Path(config["venim_path"]).expanduser()
    storage_dir.mkdir(exist_ok=True, parents=True)
    for fname in dirlist.filename:
        print(f"Downloading {fname}")
        url = level_urls[level] / rev / fname
        print(url)
        urlretrieve(str(url), storage_dir, use_tqdm=False)


def _download(url, savepath):
    # urlretrieve(str(url), savepath)
    r = requests.get(str(url), stream=True)
    with open(savepath, "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)


def download_list_of_urls(savedir, urllist, force=False, test=False, verbose=False):
    savedir.mkdir(exist_ok=True, parents=True)
    if test:
        print("The following files would be downloaded:")
    for url in tqdm(urllist):
        savepath = savedir / url.name
        if savepath.exists() and not force:
            continue
        if verbose:
            print(f"Downloading\n{url}")
            print(f"to\n{savepath}")
        if not test:
            _download(url, savepath)


class Downloader:
    def __init__(self, level="calibrated"):
        self._level = level

    @property
    def level(self):
        return [key for key in level_urls.keys() if key.startswith(self._level)][0]

    @level.setter
    def level(self, new_level):
        try:
            new_level = [key for key in level_urls.keys() if key.startswith(new_level)][
                0
            ]
        except IndexError:
            raise ValueError(
                f"New level name '{new_level}' not supported. Needs to be one of {list(level_urls.keys())}."
            )
        self._level = new_level

    def get_orbit_filelist(self, orbit):
        df = get_rev_filelist(orbit, self.level)
        self.filelist = df
        return df

    @property
    def savedir(self):
        pm = IR2PathManager()
        return pm.instr_savedir / self.level

    def urls_for_orbit(self, orbit):
        df = self.get_orbit_filelist(orbit)
        urls = level_urls[self.level] / orbit / df.filename
        return urls

    def download_orbit_files(self, orbit, only_fits=True, **kwargs):
        urls = self.urls_for_orbit(orbit)
        if only_fits:
            urls = [url for url in urls if url.suffix.endswith(".fit")]
        orbit_savedir = self.savedir / orbit
        download_list_of_urls(orbit_savedir, urls, **kwargs)


class IR2FileName:
    def __init__(self, fname):
        self.name = Path(fname).name

    @property
    def tokens(self):
        return self.name.split("_")

    @property
    def instr(self):
        return self.tokens[0]

    @property
    def datestr(self):
        return self.tokens[1]

    @property
    def date(self):
        return pd.to_datetime(self.datestr)

    @property
    def timestr(self):
        return self.tokens[2]

    @property
    def time(self):
        return pd.to_datetime(self.timestr)

    @property
    def datetime(self):
        return pd.to_datetime(self.datestr + self.timestr)

    @property
    def wavelength(self):
        return self.tokens[3]

    @property
    def level(self):
        return self.tokens[4]

    @property
    def version(self):
        return self.tokens[5]


class IR2PathManager(PathManager):
    """Class to manage files for Akatsuki IR2 data.

    Parameters
    ----------
    level : {'raw', 'calibrated', 'geom'}
        Which IR2 data to choose from.
    full_paths : bool, optional
        Switch to show full paths on disk.
    """

    def __init__(self, level="calibrated", orbit=None, full_paths=False):
        super().__init__("akatsuki", "ir2")
        self.level = level
        self.orbit = orbit
        self.full_paths = full_paths

    @property
    def orbit(self):
        return self._orbit

    @orbit.setter
    def orbit(self, new_orbit):
        if new_orbit is None:
            self._orbit = None
            return
        if not str(new_orbit).startswith("r"):
            new_orbit = "r" + str(new_orbit).zfill(4)
        self._orbit = new_orbit

    def list_files_for_orbit(self, orbit=None, full_paths=None):
        if orbit is None:
            orbit = self.orbit
        if full_paths is None:
            full_paths = self.full_paths
        if not str(orbit).startswith("r"):
            orbit = "r" + str(orbit).zfill(4)
        filelist = list((self.savedir / orbit).glob("*.fit*"))
        if not full_paths:
            filelist = [f.name for f in filelist]
        df = pd.DataFrame(filelist, columns=["filename"])
        df["datetime"] = df.filename.map(lambda x: IR2FileName(x).datetime)
        return df

    def get_path(self, index):
        filelist = self.list_files_for_orbit(full_paths=True)
        return filelist.filename.iloc[index]

    def get_label(self, index):
        p = self.get_path(index)
        return pvl.load(str(p.with_suffix(".lbl")))

    @property
    def savedir(self):
        return self.instr_savedir / self.level

    @property
    def raw_savedir(self):
        return self.instr_savedir / "raw"

    @property
    def calibrated_savedir(self):
        return self.instr_savedir / "calibrated"

    @property
    def geometry_savedir(self):
        return self.instr_savedir / "geometry"
