from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
import toml
from urlpath import URL

from planetarypy.utils import download

level_urls = {
    "l1": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_0001/data/"),
    "l2": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_1001/data/l2b/"),
    "l3": URL("https://atmos.nmsu.edu/PDS/data/vcoir2_2001/browse/"),
}


def set_venim_storage_path():
    path = input("Provide path where VENIM data should be stored:")
    config = {}
    config["venim_path"] = path
    with configpath.open("w") as f:
        toml.dump(config, f)


configpath = Path("~/.venim_config.toml").expanduser()

if not configpath.exists():
    set_venim_storage_path()
else:
    with configpath.open() as f:
        config = toml.load(f)


def get_rev_filelist(rev, level="l2"):
    results = pd.read_html(str(level_urls[level] / rev), skiprows=2)
    df = results[0]
    df = df.drop("Unnamed: 0", axis=1).dropna(how="all")
    df.columns = ["filename", "time", "size", "unnamed"]
    return df[["filename", "time", "size"]]


def download_rev(rev, level="l2"):
    dirlist = get_rev_filelist(rev)
    storage_dir = Path(config["venim_path"]).expanduser()
    storage_dir.mkdir(exist_ok=True, parents=True)
    for fname in dirlist.filename:
        print(f"Downloading {fname}")
        url = level_urls[level] / rev / fname
        print(url)
        download(str(url), storage_dir, use_tqdm=False)
