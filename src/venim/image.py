# -*- coding: utf-8 -*-
"""Tools to work with images.
"""
import circle_fit as cf
import holoviews as hv
import numpy as np
import pandas as pd
from astropy.io import fits
from holoviews import opts
from skimage.exposure import equalize_adapthist as equalize
from skimage.exposure import rescale_intensity

hv.extension("bokeh")
opts.defaults(
    opts.Image(tools=["hover"], cmap="gray"),
    opts.Points(color="red", marker="x", size=20),
)


class Image:
    def __init__(self, path):
        self.path = path
        self.data, self.header = fits.getdata(path, header=True)

    @property
    def name(self):
        return self.path.name

    @property
    def wavelength(self):
        return self.header["FILTER"]

    @property
    def exposure(self):
        return self.header["EXPOSURE"]

    @property
    def imagetime(self):
        return self.header["DATE-OBS"]

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

    def plot(self, sqrt=False, pmin=1, pmax=99, with_fit=False):
        data = self.full_frame
        data[data < 0] = np.nan
        if sqrt:
            data = np.sqrt(data)
        vmin, vmax = np.percentile(data[~np.isnan(data)], (pmin, pmax))
        if sqrt:
            data = np.sqrt(data)
        img = hv.Image(
            (np.arange(1024), np.arange(1024), data),
            label=f"{self.plot_title}, VRange: {pmin}-{pmax} %",
        ).opts(clim=(vmin, vmax), frame_height=500, frame_width=500,)
        if with_fit:
            return img * self.circle_fit
        else:
            return img

    @property
    def plot_title(self):
        t = f"{self.imagetime}, Filter: {self.wavelength}, Exp: {self.exposure} s"
        return t

    def plot_equalized(self):
        return hv.Raster(self.equalized).redim.range(z=(0, None))

    def annotate(self):
        points = hv.Points([]).opts(width=500, height=500, padding=0, responsive=False)
        self.annotator = hv.annotate.instance()
        layout = self.annotator(
            self.plot().opts(frame_height=400, frame_width=400,) * points,
            name="Limb Points",
        )
        return layout

    @property
    def circle_fit(self):
        xCtr, yCtr, r, _ = cf.least_squares_circle(self.points_data.values)
        return hv.Ellipse(xCtr, yCtr, 2 * r).opts(color="red")

    @property
    def points_data(self):
        try:
            return self.annotator.annotated.dframe()
        except AttributeError:
            return pd.DataFrame({"x": [], "y": []})

    @property
    def points_path(self):
        return self.path.with_suffix(".csv")

    def store_points(self):
        self.points_data.to_csv(self.points_path, index=False)

    def get_stored_points(self):
        return pd.read_csv(self.points_path)
