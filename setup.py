import pathlib
import setuptools
from distutils.core import setup

from distutils.extension import Extension

extensions = Extension('fugashi', 
        ['fugashi/fugashi.pyx'], 
        libraries=['mecab'])

setup(name='fugashi', 
      version='0.1.5',
      author="Paul O'Leary McCann",
      author_email="polm@dampfkraft.com",
      description="A Cython wrapper for MeCab",
      long_description=pathlib.Path('README.md').read_text(),
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
      setup_requires=['wheel', 'Cython'])
