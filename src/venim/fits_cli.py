# -*- coding: utf-8 -*-

"""Console script for venim."""

import fire

from venim.utils import write_out_fits_headers


def main():
    fire.Fire(write_out_fits_headers)
