# -*- coding: utf-8 -*-
"""Akatsuki IR2 utilities.

Utilities to download and manage Akatsuki IR2 data from NASA's PDS.
"""
import webbrowser
from pathlib import Path
from urllib.request import urlretrieve

import holoviews as hv
import numpy as np
import pandas as pd
import pvl
import requests
from astropy.io import fits
from holoviews import opts
from skimage.exposure import equalize_adapthist as equalize
from skimage.exposure import rescale_intensity
from tqdm.auto import tqdm
from urlpath import URL

from ..config import config
from ..pathmanager import PathManager

hv.extension("bokeh")
opts.defaults(
    opts.Image(tools=["hover"], cmap="gray", width=500, height=500),
    opts.Points(color="red", marker="x"),
)

storage_root = Path(config["venim_path"]).expanduser()
storage_root.mkdir(exist_ok=True, parents=True)

level_urls = {
    "raw": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_0001/data/"),
    "calibrated": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_1001/data/l2b/"),
    "geom": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_2001/geometry/"),
}

doc_urls = {
    "imagecoord": URL(
        "https://atmos.nmsu.edu/PDS/data/vcoir2_1001/document/imagecoord.txt"
    ),
    "fits_dic": URL(
        "https://atmos.nmsu.edu/PDS/data/vcoir2_1001/document/vco_fits_dic_v05.html"
    ),
    "ir2cal": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_1001/document/ir2cal.txt"),
    "onlabels": URL(
        "https://atmos.nmsu.edu/PDS/data/vcoir2_1001/document/onlabels.txt"
    ),
    "vco_observation_program": URL(
        "https://atmos.nmsu.edu/PDS/data/vcoir2_1001/document/vco_obsprg_v04.html"
    ),
}

HEADER_KEYWORDS = ["EXPOSURE", "NAXIS1", "NAXIS2", "I2_T_C1", "I2_T_C2", "I2_T_OP"]


def get_rev_filelist(rev, level="calibrated"):
    """Scrape PDS file listing using pandas.read_html.

    First scrape, using `pd.read_html`, and then add columns `datestr`, `timestr`, and
    `datetime`.

    Parameters
    ----------
    rev : str
        Revolution (i.e. orbit) string in format `rxxxx`
    level : {'raw', 'calibrated','geom'}, optional.
        Data level to parse directory for. Default: 'calibrated'

    Returns
    -------
    pd.DataFrame
        DataFrame with the content of the parsed file listing.
    """
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
    def __init__(self, level="calibrated", orbit=None):
        """Downloader class for Akatsuki IR2 data.

        The orbit can be set at creation of a Downloader object, or set later.

        Examples
        --------
        >>> dl = Downloader(orbit=25)
        >>> dl.orbit
        25

        or

        >>> dl = Dowloader()
        >>> dl.orbit = 25
        >>> dl.orbit
        25

        Parameters
        ----------
        level : {'raw','calibrated','geom}
            Akatsuki data kind to work with
        orbit : str, int
            The Akatsuki orbit. Both an integer and the revolution string 'rxxxx' is allowed.
        """
        self._level = level
        self.orbit = orbit

    @property
    def orbit(self):
        """str: Akatsuki's revolution string with format 'rxxxx'.

        The setter method takes both the int and str version as new value.
        """
        return self._orbit

    @orbit.setter
    def orbit(self, new_orbit):
        if new_orbit is None:
            self._orbit = None
            return
        if not str(new_orbit).startswith("r"):
            new_orbit = "r" + str(new_orbit).zfill(4)
        self._orbit = new_orbit

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

    def get_orbit_filelist(self, orbit=None):
        if orbit is None:
            orbit = self.orbit
        else:
            self.orbit = orbit
        df = get_rev_filelist(self.orbit, self.level)
        self.filelist = df
        return df

    @property
    def savedir(self):
        pm = IR2PathManager()
        return pm.instr_savedir / self.level

    def get_urls_for_orbit(self, orbit=None):
        if orbit is None:
            orbit = self.orbit
        else:
            self.orbit = orbit
        df = self.get_orbit_filelist(self.orbit)
        urls = [
            level_urls[self.level] / self.orbit / filename for filename in df.filename
        ]
        return pd.Series(urls)

    def download_orbit_files(self, orbit=None, only_fits=True, **kwargs):
        if orbit is None:
            orbit = self.orbit
        else:
            self.orbit = orbit
        urls = self.get_urls_for_orbit(orbit)
        if only_fits:
            urls = [url for url in urls if url.suffix.endswith(".fit")]
        orbit_savedir = self.savedir / self.orbit
        download_list_of_urls(orbit_savedir, urls, **kwargs)


class IR2FileName:
    """Class to dismantle an IR2FileName.

    Each splittable part of the filename is reachable as a class attribute, and the
    datestr and timestr data has been used to create a `pandas.Timestamp`, which can
    easily be converted back to a datetime object.

    Example
    -------
    >>> irfn = IR2FileName('ir2_20160829_201008_202_l2b_v10.fit')
    >>> irfn.wavelength
    202
    >>> irfn.datetime
    Timestamp('2016-08-29 20:10:08')

    Parameters
    ----------
    fname : str
        Akatsuki filename in the format `ir2_20160829_201008_202_l2b_v10.fit`
    """

    def __init__(self, fname):
        self.name = Path(fname).name

    @property
    def tokens(self):
        "list: Parts of the filename, separated by '_'."
        return self.name.split("_")

    @property
    def instr(self):
        "str: Instrument ID."
        return self.tokens[0]

    @property
    def datestr(self):
        "str: The date string of the filename."
        return self.tokens[1]

    @property
    def date(self):
        "pd.Timestamp: Date string converted to proper time object."
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
    def in_micron(self):
        "float: Filter wavelength converted to micron."
        return int(self.wavelength) / 100

    @property
    def level(self):
        return self.tokens[4]

    @property
    def version(self):
        return self.tokens[5]

    def __str__(self):
        s = f"IR2 FileName {self.name}\n"
        s += f"DateTime: {self.datetime}\n"
        s += f"Wavelength: {self.in_micron} micron.\n"
        s += f"Level: {self.level}\n"
        s += f"Version: {self.version}\n"
        return s

    def __repr__(self):
        return self.__str__()


class IR2PathManager(PathManager):
    """Class to manage files for Akatsuki IR2 data.

    Offers method `list_files_for_orbit` to get a list of found files per orbit in
    form of a pandas.DataFrame.
    Parameters
    ----------
    level : {'raw', 'calibrated', 'geom'}
        Which IR2 data to choose from.
    orbit : int, str; optional
        Akatsuki orbit, both revolution string rxxxx and integer number is allowed.
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
        """str: Akatsuki orbit in format of revolution string 'rxxxx'."""
        return self._orbit

    @orbit.setter
    def orbit(self, new_orbit):
        if new_orbit is None:
            self._orbit = None
            return
        if not str(new_orbit).startswith("r"):
            new_orbit = "r" + str(new_orbit).zfill(4)
        self._orbit = new_orbit

    def list_files_for_orbit(self, orbit=None):
        """Get a file listing as a pandas.DataFrame.

        Parameters
        ----------
        orbit : str, int
            Akatsuki orbit, either as rxxxx string or integer.
        full_paths : bool
            Switch to show either truncated or pull paths.

        Returns
        -------
        pandas.DataFrame
            The Dataframe lists filenames and the datetimes for the files.
        """
        if orbit is None:
            orbit = self.orbit
        pathlist = list((self.savedir).glob("*.fit*"))
        namelist = [f.name for f in pathlist]
        df = pd.DataFrame({"filename": namelist, "full_path": pathlist})
        df["datetime"] = df.filename.map(lambda x: IR2FileName(x).datetime)
        df["wavelength"] = df.filename.map(lambda x: int(IR2FileName(x).wavelength))
        df = pd.concat([df, df.apply(get_header_keywords, axis=1)], axis=1)
        # for keyword in HEADER_KEYWORDS:
        #     df[keyword] = df.full_path.map(lambda x: fits.open(x)[1].header[keyword])
        columns = list(df.columns)
        columns.remove("full_path")
        columns.append("full_path")
        return df[columns].set_index("datetime")

    def get_path(self, index):
        ""
        filelist = self.list_files_for_orbit(full_paths=True)
        return filelist.filename.iloc[index]

    def get_label(self, index):
        p = self.get_path(index)
        return pvl.load(str(p.with_suffix(".lbl")))

    @property
    def savedir(self):
        try:
            return self.instr_savedir / self.level / self.orbit
        except TypeError:
            raise ValueError("Orbit must be set first.")


# helper functions
def get_header_keywords(row):
    header = fits.open(row.full_path)[1].header
    d = {}
    for kw in HEADER_KEYWORDS:
        d[kw] = header[kw]
    return pd.Series(d)


def get_exposure(row):
    fits.open(row.full_path)[1].header[""]


def get_orbit_file_list(orbit):
    "Shortcut to simply get the list of files from IR2PathManager."
    pm = IR2PathManager(orbit=orbit)
    return pm.list_files_for_orbit()


def get_file_path(id):
    """
    Glob all IR2 data for given file name.

    Parameters
    ----------
    id : str
        IR2 filename

    Returns
    -------
    pathlib.Path
        Local path to filename given.
    """
    pm = IR2PathManager(orbit=0)
    return list(pm.savedir.parent.glob(f"*/{id}"))[0]


def get_file_header(id):
    """
    Get header for given file name.

    Searches all IR2 data for given filename and returns header of found file.

    Parameters
    ----------
    id : str
        IR2 filename.

    Returns
    -------
    fits.Header
        FITS ImageHDU header for given filename.
    """
    p = get_file_path(id)
    return fits.open(p)[1].header


def get_file_data(id):
    """
    Get data for given file name.

    Searches all IR2 data for given filename and returns numpy data for found file.

    Parameters
    ----------
    id: str
        IR2 filename.

    Returns
    -------
    numpy.array
        Numpy 2D array of ImageHDU of the FITS file for given filename.
    """
    p = get_file_path(id)
    return fits.getdata(p)


def getdata(id, header=False):
    """
    Simulate fits.getdata, for just a filename without full path.
    Will search all IR2 data for given file name.

    Parameters
    ----------
    id : str
        File name
    header : bool, optional
        Boolean switch to control if you also want the header. Default: False

    Returns
    -------
    numpy.array(, fits.Header)
        Return numpy.array (for ImageHDU), and optionally also the fits.Header
    """
    p = Path(id)
    if not p.is_absolute():
        p = get_file_path(id)
    return fits.getdata(p, header=header)


def list_available_doc_urls():
    "List the available URLs to IR2 documentation on PDS."
    for k, v in doc_urls.items():
        print(k)
        print(v)


def open_doc_url(doc_key):
    webbrowser.open_new(str(doc_urls[doc_key]))


def open_fits_dic():
    "Open new browser tab for FITS DIC."
    open_doc_url("fits_dic")


class Image:
    def __init__(self, id):
        p = Path(id)
        if not p.is_absolute():
            p = get_file_path(id)
        self.path = p
        self.data, self.header = fits.getdata(p, header=True)

    @property
    def name(self):
        return self.p.name

    @property
    def full_frame(self):
        newimg = np.zeros((1024, 1024))
        ll_row = self.header["P_POSLLY"] - 1
        ll_col = self.header["P_POSLLX"] - 1
        ur_row = self.header["P_POSURY"]
        ur_col = self.header["P_POSURX"]
        newimg[ll_row:ur_row, ll_col:ur_col] = self.data
        return newimg

    @property
    def rescaled(self):
        return rescale_intensity(self.full_frame, out_range="float")

    @property
    def equalized(self):
        return equalize(self.rescaled)

    def plot(self):
        return hv.Image(
            (np.arange(1024), np.arange(1024), self.full_frame)
        ).redim.range(z=(0, None))

    def plot_equalized(self):
        return hv.Raster(self.equalized).redim.range(z=(0, None))

    def annotate(self):
        points = hv.Points([]).opts(
            width=500, height=500, padding=0, responsive=False, size=20
        )
        self.annotator = hv.annotate.instance()
        layout = self.annotator(self.plot() * points, name="Limb Points")
        return layout

    @property
    def points_data(self):
        try:
            return self.annotator.annotated.dframe()
        except AttributeError:
            print("Got to annotate first")
