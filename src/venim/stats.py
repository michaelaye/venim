from pathlib import Path

import astropy.io.fits as pf
import pandas as pd
from tqdm.auto import tqdm

irtf_translator = {
    "name": "IRAFNAME",
    "date": "DATE_OBS",
    "time": "TIME_OBS",
}


def scan_image_directory(path):
    """Scan directory of FITS files to create basic stats.

    Creates CSV file ready to be read by pandas and print-out of the stats if
    less than 100 entries.

    Parameters
    ----------
    path : str, pathlib.Path

    Returns
    -------
    pd.DataFrame
        DataFrame containing the collected stats
    """
    input_dir = Path(path)
    directory_file = input_dir / "directory.csv"
    files = list(input_dir.glob("*.fits"))

    print(len(files), "images found.")

    # fields = [
    #     "name",
    #     "date",
    #     "time",
    #     "filter",
    #     "exposure",
    #     "hasSlit",
    #     "isValid",
    #     "angle",
    #     "radius",
    #     "area",
    #     "centerY",
    #     "centerX",
    #     "sublon",
    #     "sublat",
    #     "isFull",
    #     "group",
    # ]

    bucket = []

    print("Scanning directory...")
    for fitspath in tqdm(files):
        _, head = pf.getdata(fitspath, header=True)
        line = {}
        line["name"] = fitspath.name
        line["date"] = head["DATE_OBS"]
        line["time"] = head["TIME_OBS"]
        line["filter"] = head["GFLT"]
        line["exposure"] = head["ELAPTIME"]
        line["hasSlit"] = head["SLIT"] != "Mirror"
        line["isValid"] = head["ELAPTIME"] == 0.482500 and head["GFLT"] == "contK"
        bucket.append(line)

    df = pd.DataFrame(bucket)
    df.to_csv(directory_file)
    print("Metadata CSV generated at", directory_file)
    return df
