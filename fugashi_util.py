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
    if os.name == 'nt':
        win_mecab_dir = r'C:\mecab'
        mecab_details = (win_mecab_dir, win_mecab_dir, 'libmecab')
        data_files = [("lib\\site-packages\\", ["{}\\libmecab.dll".format(win_bin_dir)])]
        return mecab_details, data_files

def mecab_config_cygwin():
    base_dir = os.getcwd()
    os.makedirs("build/mecab", exist_ok=True)
    os.chdir("build/mecab")
    ## Cygwin
    if platform.system().startswith("CYGWIN"):
        rep = "mecab-cygwin64" if platform.machine() == "x86_64" else "mecab-cygwin32"
        subprocess.run(["git", "clone", "--depth=1", "https://github.com/KoichiYasuoka/"+rep])
        os.chdir(rep)
        subprocess.run(["sh", "-x", "./install.sh", "/usr/local"])
        output = mecab_config("/usr/local/bin/mecab-config")
        return output, []

def mecab_config_debian():
    ## Debian
    # XXX how is this different from the debian2 part?
    try:
        subprocess.run(["apt-get", "install", "-y", "libmecab-dev"])
        output = mecab_config("mecab-config")
        return output, []
    except:
        pass

def mecab_config_debian2():
    ##XXX What platform is this? Also Debian?
    os.chdir(base_dir+"/build/mecab")
    subprocess.run(["git", "clone", "--depth=1", "https://github.com/taku910/mecab"])
    os.chdir("mecab/mecab")
    try:
        subprocess.run(["apt-get", "download", "libmecab-dev", "libmecab2"])
        for deb in glob.glob("libmecab*.deb"):
            subprocess.run(["dpkg", "-x", deb, "."])
        output = mecab_config("usr/bin/mecab-config").replace("/usr/","build/mecab/usr/")
        os.chdir(base_dir)
        mc = output.split("\n")
        lib_dir = site.USER_BASE + "/lib/mecab"
        mecab_details = (*mc, '-Wl,-rpath={}'.format(lib_dir))
        data_files = [(lib_dir, glob.glob(mc[1] + "/libmecab.*"))]
        return mecab_details, data_files
    except:
        pass

def mecab_config_linux_build():
    # this builds mecab from source on a linux-like (OSX?)
    # XXX what platform is this for?
    os.chdir(base_dir+"/build/mecab")
    subprocess.run(["git", "clone", "--depth=1", "https://github.com/taku910/mecab"])
    os.chdir("mecab/mecab")
    if not os.path.isfile("mecab-config"):
        for f in ["aclocal.m4", "config.h.in", "configure", "Makefile.in", "src/Makefile.in"]:
            subprocess.run(["touch", f])
            subprocess.run(["sleep", "1"])
        subprocess.run(["./configure", "--disable-static", "--enable-shared", "--with-charset=utf8"])
    os.chdir("src")
    subprocess.run(["make", "libmecab.la"])
    if not os.path.isfile("libmecab.so"):
        os.symlink(".libs/libmecab.so", "libmecab.so")
    src_dir = "build/mecab/mecab/mecab/src"
    obj= " ".join(glob.glob(".libs/*.o")).replace(".libs/", src_dir+"/.libs/")
    mecab_details = (src_dir, '', 'stdc++', obj)
    return mecab_details, []

def check_libmecab():
    """Get MeCab build parameters.

    Where available the mecab-config script is used, but if it's available it
    will be installed or the parameters will otherwise be figured out."""

    configs = [
            mecab_config_windows,
            mecab_config,
            mecab_config_cygwin,
            mecab_config_debian,
            mecab_config_debian2,
            mecab_config_linux_build,
            ]

    # A few scripts will use a build directory. Save where we start so we can
    # reset the directory after each build step.
    cwd = os.getcwd()
    for config in configs:
        try:
            out = config()
            if out:
                return out
        except:
            # failure is normal, typically just a different platform
            pass
        finally:
            os.chdir(cwd)
