import astropy.io.fits as pf
from pathlib import Path
import os
from tqdm import tqdm_notebook as tqdm


def scan_image_directory(path):
    input_dir = Path(path)
    directory_file = Path("../pipeline_demo/directory.csv")
    files = list(input_dir.glob("*.fits"))
    print(len(files), "images found.")

    fields = [
        "name",
        "date",
        "time",
        "filter",
        "exposure",
        "hasSlit",
        "isValid",
        "angle",
        "radius",
        "area",
        "centerY",
        "centerX",
        "sublon",
        "sublat",
        "isFull",
        "group",
    ]

    bucket = []

    print("Scanning directory...")
    for fitspath in tqdm(files):
        _, head = pf.getdata(fitspath, header=True)
        line = {}
        line['name'] = fitspath.name
        line['date'] = head['DATE_OBS']
        line['time'] = head['TIME_OBS']
        line['filter'] = head['GFLT']
        line['exposure'] = head['ELAPTIME']
        line['hasSlit'] = (head['SLIT'] != 'Mirror')
        line['isValid'] = (head["ELAPTIME"] == 0.482500 and head["GFLT"] == "contK")
        bucket.append(line)

    df = pd.DataFrame(bucket)
    df.to_csv(directory_file)
    print("Metadata CSV generated at", directory_file)

