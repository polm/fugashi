import os
import pathlib
import sys

import setuptools
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

from fugashi_util import check_libmecab

# get the build parameters
output, dll_files = check_libmecab()

# pad the list in case something's missing
mecab_config = list(output) + ([''] * 5)
include_dirs = mecab_config[0].split()
library_dirs = mecab_config[1].split()
libraries = mecab_config[2].split()
extra_objects = mecab_config[3].split()
extra_link_args = mecab_config[4].split()


# Windows DLL related prep.
# By default the DLL will be bundled on windows, but you can turn it off with
# an env var.
bundle_dll = False
fugashi_package_files = []
no_bundle_env_var = os.environ.get("FUGASHI_NO_BUNDLE_DLL", "")
if sys.platform == 'win32' and no_bundle_env_var not in ['', '0']:
    bundle_dll = True
    fugashi_package_files = [pathlib.Path(i).name for i in dll_files]

class build_ext(_build_ext):
    """Custom behavior for build_ext.

    This is only run when bundling DLLs on Windows, which requires copying
    files around."""
    def run(self):
        if bundle_dll:
            if self.editable_mode:
                fugashi_dir = pathlib.Path(__file__).parent / 'fugashi'
            else:
                fugashi_dir = pathlib.Path(self.build_lib) / 'fugashi'
            for i in dll_files:
                self.copy_file(i, fugashi_dir)
        return super().run()


extensions = Extension('fugashi.fugashi', 
        ['fugashi/fugashi.pyx'], 
        libraries=libraries,
        library_dirs=library_dirs,
        include_dirs=include_dirs,
        extra_objects=extra_objects,
        extra_link_args=extra_link_args)

setup(name='fugashi', 
      use_scm_version=True,
      author="Paul O'Leary McCann",
      author_email="polm@dampfkraft.com",
      description="A Cython MeCab wrapper for fast, pythonic Japanese tokenization.",
      long_description=pathlib.Path('README.md').read_text('utf8'),
      long_description_content_type="text/markdown",
      url="https://github.com/polm/fugashi",
      packages=setuptools.find_packages(),
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Natural Language :: Japanese",
          ],
      python_requires='>=3.8',
      ext_modules=[extensions],
      cmdclass={'build_ext': build_ext},
      package_data={'fugashi': fugashi_package_files},
      entry_points={
          'console_scripts': [
              'fugashi = fugashi.cli:main',
              'fugashi-info = fugashi.cli:info',
              'fugashi-build-dict = fugashi.cli:build_dict',
      ]},
      extras_require={
          'unidic': ['unidic'],
          'unidic-lite': ['unidic-lite'],
      },
      setup_requires=['wheel', 'Cython~=3.0.11', 'setuptools_scm'])
