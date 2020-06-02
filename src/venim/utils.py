import matplotlib
import matplotlib.pyplot as plt
from astropy.io import fits
from tqdm.auto import tqdm

from .ir2 import IR2FileName

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


def check_expection_handling():
    try:
        print(1 / 0)
    except ZeroDivisionError:
        pass
