======================
Venus Imaging Analysis
======================


.. image:: https://img.shields.io/pypi/v/venim.svg
        :target: https://pypi.python.org/pypi/venim

.. image:: https://img.shields.io/travis/michaelaye/venim.svg
        :target: https://travis-ci.org/michaelaye/venim

.. image:: https://readthedocs.org/projects/venim/badge/?version=latest
        :target: https://venim.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/michaelaye/venim/shield.svg
     :target: https://pyup.io/repos/github/michaelaye/venim/
     :alt: Updates


Python tools for Venus Image Analysis


* Free software: MIT license
* Documentation: https://venim.readthedocs.io.


Features
--------

If the feature has been implemented in an importable way, it's indicated by a filled checkmark [x]

* [x] Read FITS arrays (done via astropy.io.fits)
* [x] FITS image stats scanner (creates CSV overview file)
* [ ] Standard image reduction pipeline: bias subtraction, flat field normalization, etc.
* [ ] Other image clean-up: bad pixels, cosmic rays, detector artifacts
* [ ] Generate estimated errors for each pixel
* [ ] Transform detector x,y coordinates into local Lat, Lon
* [ ] Take various gradients of images
* [ ] Filter images in the spatial frequency domain
* [ ] Sub-pixel disk registration
* [ ] Robust stacking of co-registered images
* [ ] Cloud tracking



Credits
---------

The content of this package is based on summer science work by Nicolas Ardavin and Kenyon Prater, under the lead of Eliot Young and Mark Bullock.
Later improvements have been implemented by the package maintainer Michael Aye.


This package was created with Cookiecutter_ and the forked `michaelaye/cookiecutter-pypackage-conda`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`michaelaye/cookiecutter-pypackage-conda`: https://github.com/michaelaye/cookiecutter-pypackage-conda
