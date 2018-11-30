from setuptools import setup, find_packages
from distutils.core import Extension

DISTNAME = 'pyperc'
VERSION = '0.1.0'
PACKAGES = ['pyperc']
EXTENSIONS = []
DESCRIPTION = 'Invasion percolation'
LONG_DESCRIPTION = open('README.md').read()
AUTHOR = 'pyperc developers'
MAINTAINER_EMAIL = 'kaklise@sandia.gov'
LICENSE = 'Revised BSD'
URL = ''

setuptools_kwargs = {
    'zip_safe': False,
    'install_requires': [],
    'scripts': [],
    'include_package_data': True
}

setup(name=DISTNAME,
      version=VERSION,
      packages=PACKAGES,
      ext_modules=EXTENSIONS,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      maintainer_email=MAINTAINER_EMAIL,
      license=LICENSE,
      url=URL,
      **setuptools_kwargs)
