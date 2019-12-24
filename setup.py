import pathlib
import setuptools
import subprocess
import os
from distutils.core import setup
from distutils.extension import Extension

from fugashi_util import check_libmecab
curdir = os.getcwd()
output,data_files = check_libmecab()
os.chdir(curdir)
mecab_config = output.split("\n")
include_dirs = mecab_config[0].split()
library_dirs = mecab_config[1].split()
libraries = mecab_config[2].split()

extensions = Extension('fugashi', 
        ['fugashi/fugashi.pyx'], 
        libraries=libraries,
        library_dirs=library_dirs,
        include_dirs=include_dirs)

setup(name='fugashi', 
      version='0.1.6',
      author="Paul O'Leary McCann",
      author_email="polm@dampfkraft.com",
      description="A Cython wrapper for MeCab",
      long_description=pathlib.Path('README.md').read_text('utf8'),
      long_description_content_type="text/markdown",
      url="https://github.com/polm/fugashi",
      packages=setuptools.find_packages(),
      install_requires=['Cython'],
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Natural Language :: Japanese",
          ],
      python_requires='>=3.6',
      ext_modules=[extensions],
      data_files=data_files,
      setup_requires=['wheel', 'Cython'])
