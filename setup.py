import os
import pathlib
import sys

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

# This is a side effect of how build works, see:
# https://github.com/pypa/setuptools/discussions/3134
sys.path.append(str(pathlib.Path(__file__).parent))
from fugashi_util import check_libmecab

# get the build parameters
output, dll_files = check_libmecab()

# pad the list in case something's missing
mecab_config = list(output) + ([""] * 5)
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
should_bundle = os.environ.get("FUGASHI_NO_BUNDLE_DLL", "") in ("", "0")
if sys.platform == "win32" and should_bundle:
    bundle_dll = True
    fugashi_package_files = [pathlib.Path(i).name for i in dll_files]


class build_ext(_build_ext):
    """Custom behavior for build_ext.

    This is only run when bundling DLLs on Windows, which requires copying
    files around."""

    def run(self):
        if bundle_dll:
            if self.editable_mode:
                fugashi_dir = pathlib.Path(__file__).parent / "fugashi"
            else:
                fugashi_dir = pathlib.Path(self.build_lib) / "fugashi"
            for i in dll_files:
                self.copy_file(i, fugashi_dir)
        return super().run()


extensions = Extension(
    "fugashi.fugashi",
    ["fugashi/fugashi.pyx"],
    libraries=libraries,
    library_dirs=library_dirs,
    include_dirs=include_dirs,
    extra_objects=extra_objects,
    extra_link_args=extra_link_args,
)

setup(
    ext_modules=[extensions],
    cmdclass={"build_ext": build_ext},
    package_data={"fugashi": fugashi_package_files},
)
