import pathlib
import setuptools
import subprocess
import os
from distutils.core import setup
from distutils.extension import Extension

is_windows = os.name == 'nt'

win_mecab_dir = r'C:\mecab'
win_sdk_dir = win_mecab_dir
win_bin_dir = win_mecab_dir
# If you want to use official Windows binary, you can comment out following variables
#is_64bits = sys.maxsize > 2**32
#win_mecab_dir = r'C:\Program Files{}\MeCab'.format('' if is_64bits else ' (x86)')
#win_sdk_dir = r'{}\sdk'.format(win_mecab_dir)
#win_bin_dir = r'{}\bin'.format(win_mecab_dir)

if is_windows:
    include_dirs = [win_sdk_dir]
    library_dirs = [win_sdk_dir]
    libraries = ["libmecab"]
    data_files = [("lib\\site-packages\\", ["{}\\libmecab.dll".format(win_bin_dir)])]
else:
    try:
        output = subprocess.check_output(["mecab-config", "--inc-dir", "--libs-only-L", "--libs-only-l"])
    except:
	from .util import download_libmecab
	output = download_libmecab()
    if not isinstance(output, str):
	output = output.decode("utf-8")
    output = output.split("\n")
    include_dirs = output[0].split()
    library_dirs = output[1].split()
    libraries = output[2].split()
    data_files = []

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
