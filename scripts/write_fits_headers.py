import sys
from pathlib import Path

import pandas as pd
from astropy.io import fits

try:
    from tqdm.auto import tqdm
except ImportError:
    TQDM_NOT_FOUND = True
else:
    TQDM_NOT_FOUND = False


def find_best_header(path):
    hdul = fits.open(path)
    best_hdu = None
    while hdul:
        hdu = hdul.pop(0)
        best_hdu = hdu
        if isinstance(hdu, fits.hdu.image.ImageHDU):
            break
    return best_hdu.header


def convert_header_to_dataframe(header, index=None):
    headerdict = dict(header)
    # there's a huge empty string at the end of headers
    # if it's called "", then it's removed, otherwise no harm done.
    _ = headerdict.pop("", None)
    # remove COMMENT and ORIGIN
    keys_to_delete = ["COMMENT", "ORIGIN"]
    for key in keys_to_delete:
        _ = headerdict.pop(key, None)
    index = pd.Index([index], name="filename")
    return pd.DataFrame(pd.Series(headerdict).to_dict(), index=index)


def write_out_fits_headers(folder):
    """Writing out FITS headers into CSV.

    This function will search for FITS files in the given FOLDER.
    It then scans each FITS file for ImageHDUs, and if not there, will take any HDU's header.
    It collects all header data, removes the keys "COMMENT", "HISTORY", and "ORIGIN",
    and combines everything into a CSV file.

    Parameters
    ----------
    folder : str, pathlib.Path
        Folder in which to look for FITS files. Can be ".".

    Returns
    -------
    Nothing, but creates a CSV file named: "<FOLDER>_fits_headers.csv"
    """
    if folder is None:
        folder = Path(".").absolute()
    folder = Path(folder).absolute()
    fits_files = folder.glob("*.fits")

    bucket = []

    if TQDM_NOT_FOUND:
        for f in fits_files:
            header = find_best_header(f)
            bucket.append(convert_header_to_dataframe(header, index=f.name))
    else:
        for f in tqdm(fits_files):
            header = find_best_header(f)
            bucket.append(convert_header_to_dataframe(header, index=f.name))
    df = pd.concat(bucket)
    savename = f"{folder.name}_fits_headers.csv"
    savepath = folder / savename
    df.to_csv(savepath)
    print(f"Created {savepath}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"Usage: {sys.argv[0]} folder")
        sys.exit()
    else:
        write_out_fits_headers(sys.argv[1])
