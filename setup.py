# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in pibicut/__init__.py
from pibicut import __version__ as version

setup(
	name="pibicut",
	version=version,
	description="Frappe/ERPNext URL Shortener",
	author="PibiCo",
	author_email="pibico.sl@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
