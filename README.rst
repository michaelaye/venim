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


Features (planned)
------------------

* Read FITS arrays (done via astropy.io.fits)
* (Standard image reduction pipeline: bias subtraction, flat field normalization, etc.)
* (Other image clean-up: bad pixels, cosmic rays, detector artifacts)
* (Generate estimated errors for each pixel)
* (Transform detector x,y coordinates into local Lat, Lon)
* (Take various gradients of images)
* (Filter images in the spatial frequency domain)
* (Sub-pixel disk registration)
* (Robust stacking of co-registered images)
* (Cloud tracking)

* FITS image stats scanner (creates CSV overview file)


Credits
---------

This package was created with Cookiecutter_ and the forked `michaelaye/cookiecutter-pypackage-conda`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`michaelaye/cookiecutter-pypackage-conda`: https://github.com/michaelaye/cookiecutter-pypackage-conda
