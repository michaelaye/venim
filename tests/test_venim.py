#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `venim` package."""

from pathlib import Path
from urllib.request import urlretrieve

import pytest
from astropy.io import fits

# from click.testing import CliRunner
# from venim import cli, stats

server_url = "https://atmos.nmsu.edu/PDS/data/"
testfile_url = server_url + "vcoir2_0001/data/r0009/ir2_20160313_075709_174_l1b_v10.fit"


@pytest.fixture(scope="session")
def image_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("testimg.fits")
    print("URL", testfile_url)
    print("FN", str(fn))
    urlretrieve(str(testfile_url), str(fn))
    return fn


# @pytest.fixture
# def response():
#     """Sample pytest fixture.

#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/michaelaye/cookiecutter-pypackage-conda')


# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string


# def test_command_line_interface():
#     """Test the CLI."""
#     runner = CliRunner()
#     result = runner.invoke(cli.main)
#     assert result.exit_code == 0
#     assert 'venim.cli.main' in result.output
#     help_result = runner.invoke(cli.main, ['--help'])
#     assert help_result.exit_code == 0
#     assert '--help  Show this message and exit.' in help_result.output
