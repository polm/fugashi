import os
import platform
import site
import subprocess
import glob

def mecab_config(com="mecab-config"):
    output = subprocess.check_output([com, "--inc-dir", "--libs-only-L", "--libs-only-l"])
    if not isinstance(output, str):
        output = output.decode("utf-8")
    return output.split('\n'), []

def mecab_config_windows():
    ## Windows
    if not os.name == 'nt':
        return

    win_mecab_dir = r'C:\mecab'
    win_bin_dir = win_mecab_dir # this is separate from the sdk dir on some installs
    mecab_details = (win_mecab_dir, win_mecab_dir, 'libmecab')
    data_files = [("lib\\site-packages\\fugashi\\", ["{}\\libmecab.dll".format(win_bin_dir)])]
    return mecab_details, data_files

def mecab_config_cygwin():
    ## Cygwin
    os.chdir("build/mecab")
    if platform.system().startswith("CYGWIN"):
        rep = "mecab-cygwin64" if platform.machine() == "x86_64" else "mecab-cygwin32"
        subprocess.run(["git", "clone", "--depth=1", "https://github.com/KoichiYasuoka/"+rep])
        mecab_details = ("build/mecab/"+rep+"/include", "build/mecab/"+rep+"/lib", "mecab stdc++")
        return mecab_details, []

def mecab_config_debian_root():
    ## Debian (as root)
    subprocess.run(["apt-get", "install", "-y", "libmecab-dev"])
    output = mecab_config("mecab-config")
    return output

def mecab_config_debian_user():
    ## Debian (as user)
    base_dir = os.getcwd()
    os.chdir("build/mecab")
    subprocess.run(["apt-get", "download", "libmecab-dev", "libmecab2"])
    for deb in glob.glob("libmecab*.deb"):
        subprocess.run(["dpkg", "-x", deb, "."])
    mc,dummy = mecab_config("usr/bin/mecab-config")
    os.chdir(base_dir)
    lib_dir = site.USER_BASE + "/lib/mecab"
    mecab_details = ("build/mecab" + mc[0], "build/mecab" + mc[1], mc[2], '-Wl,-rpath={}'.format(lib_dir))
    data_files = [(lib_dir, glob.glob("build/mecab" + mc[1] + "/libmecab.*"))]
    return mecab_details, data_files

def mecab_config_linux_build():
    """Build from source on Linux-like as a last resort."""
    base_dir = os.getcwd()
    os.chdir("build/mecab")
    subprocess.run(["git", "clone", "--depth=1", "https://github.com/taku910/mecab"])
    os.chdir("mecab/mecab")
    if not os.path.isfile("mecab-config"):
        for f in ["aclocal.m4", "config.h.in", "configure", "Makefile.in", "src/Makefile.in"]:
            subprocess.run(["touch", f])
            subprocess.run(["sleep", "1"])
        subprocess.run(["./configure", "--disable-static", "--enable-shared", "--with-charset=utf8"])
    os.chdir("src")
    subprocess.run(["make", "libmecab.la"])
    src_dir = "build/mecab/mecab/mecab/src"
    lib_dir = site.USER_BASE + "/lib/mecab"
    if os.path.isfile("libmecab.so"):
        os.chdir(base_dir)
        data_files = [(lib_dir, glob.glob(src_dir + "/libmecab.*"))]
    else:
        os.symlink(".libs/libmecab.so", "libmecab.so")
        os.chdir(base_dir)
        data_files = [(lib_dir, glob.glob(src_dir + "/.libs/libmecab.*"))]
    if platform.platform().startswith("Darwin"):
        lib_arg = "-rpath {} -stdlib=libc++ -mmacosx-version-min=10.9".format(lib_dir)
    else:
        lib_arg = "-Wl,-rpath={}".format(lib_dir)
    mecab_details = (src_dir, src_dir, 'mecab stdc++', lib_arg)
    return mecab_details, data_files

def check_libmecab():
    """Get MeCab build parameters.

    Where available the mecab-config script is used, but if it's available it
    will be installed or the parameters will otherwise be figured out."""

    configs = [
            mecab_config_windows,
            mecab_config,
            mecab_config_cygwin,
            mecab_config_debian_root,
            mecab_config_debian_user,
            mecab_config_linux_build,
            ]

    # A few scripts will use a build directory. Save where we start so we can
    # reset the directory after each build step.
    cwd = os.getcwd()
    os.makedirs("build/mecab", exist_ok=True)
    for config in configs:
        try:
            out = config()
            os.chdir(cwd)
            if out:
                return out
        except:
            # failure is normal, typically just a different platform
            os.chdir(cwd)
    return [], []
