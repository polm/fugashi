import pathlib
import setuptools
import subprocess
from distutils.core import setup
from distutils.extension import Extension

from fugashi_util import check_libmecab

# get the build parameters
output, data_files = check_libmecab()

# pad the list in case something's missing
mecab_config = list(output) + ([''] * 5)
include_dirs = mecab_config[0].split()
library_dirs = mecab_config[1].split()
libraries = mecab_config[2].split()
extra_objects = mecab_config[3].split()
extra_link_args = mecab_config[4].split()

extensions = Extension('fugashi', 
        ['fugashi/fugashi.pyx'], 
        libraries=libraries,
        library_dirs=library_dirs,
        include_dirs=include_dirs,
        extra_objects=extra_objects,
        extra_link_args=extra_link_args)

setup(name='fugashi', 
      version='0.1.10rc2',
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
      python_requires='>=3.5',
      ext_modules=[extensions],
      data_files=data_files,
      extras_require={'unidic': ['unidic']},
      setup_requires=['wheel', 'Cython'])
