from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from astropy.io import fits
from tqdm.auto import tqdm

from .akatsuki.ir2 import IR2FileName

matplotlib.use("agg")


def create_preview(path):
    data, h = fits.getdata(path, header=True)
    fn = IR2FileName(path.name)
    fig, ax = plt.subplots()
    ax.imshow(data, vmin=0, cmap="gray", origin="lower")
    savename = path.with_suffix(".png")
    ax.set_title(f"{fn.datetime}, exp: {h['EXPOSURE']}, filter: {fn.wavelength}")
    fig.savefig(savename, dpi=150)
    plt.close(fig)


def create_browse_images(filelist):
    for p in tqdm(filelist.full_path):
        try:
            create_preview(p)
        except ValueError:
            print(f"problem with {p.name}")


def find_best_header(path):
    hdul = fits.open(path)
    best_hdu = None
    while hdul:
        hdu = hdul.pop(0)
        best_hdu = hdu
        if isinstance(hdu, fits.hdu.image.ImageHDU):
            break
    return best_hdu.header


def clean_header(header):
    headerdict = dict(header)
    # there's a huge empty string at the end of headers
    # if it's called "", then it's removed, otherwise no harm done.
    _ = headerdict.pop("", None)
    # remove COMMENT and ORIGIN
    keys_to_delete = ["COMMENT", "ORIGIN", "HISTORY"]
    for key in keys_to_delete:
        _ = headerdict.pop(key, None)
    return headerdict


def convert_header_to_dataframe(header, index=None):
    headerdict = dict(header)
    index = pd.Index([index], name="filename")
    headerdict = clean_header(header)
    return pd.DataFrame(pd.Series(headerdict).to_dict(), index=index)


def get_data_frame(fits_files, folder):
    bucket = []

    for f in fits_files:
        header = find_best_header(f)
        bucket.append(convert_header_to_dataframe(header, index=f.name))
    df = pd.concat(bucket)
    savename = f"{folder.name}_fits_headers.csv"
    savepath = folder / savename
    df.to_csv(savepath)


def write_out_fits_headers(folder, single_file=False):
    """Writing out FITS headers into CSV.

    This function will search for FITS files in the given FOLDER.
    It then scans each FITS file for ImageHDUs, and if not there, will take any HDU's header.
    It collects all header data, removes the keys "COMMENT", "HISTORY", and "ORIGIN",
    and combines everything into a CSV file.

    Parameters
    ----------
    folder : str, pathlib.Path
        Folder in which to look for FITS files. Can be ".".
    single_file : bool, optional
        Switch to write out a header file for each FITS file separately.

    Returns
    -------
    Nothing, but creates a CSV file named: "<FOLDER>_fits_headers.csv"
    """
    if folder is None:
        folder = Path(".").absolute()
    folder = Path(folder).absolute()
    fits_files = folder.glob("*.fits")

    if single_file:
        for path in fits_files:
            header = find_best_header(path)
            savename = f"{path.stem}_header.txt"
            savepath = path.with_name(savename)
            header.totextfile(str(savepath))
    else:
        get_data_frame(fits_files, folder)
