import setuptools
from distutils.core import setup

from distutils.extension import Extension
from Cython.Build import cythonize

extensions = Extension('fugashi', 
        ['fugashi/fugashi.pyx'], 
        libraries=['mecab'])
setup(name='fugashi', 
      version='0.1.0',
      author="Paul O'Leary McCann",
      author_email="polm@dampfkraft.com",
      description="A Cython wrapper for MeCab",
      url="https://github.com/polm/fugashi",
      packages=setuptools.find_packages(),
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Natural Language :: Japanese",
          ],
      python_requires='>=3.6',
      ext_modules=cythonize(extensions),
      setup_requires=['wheel'])
