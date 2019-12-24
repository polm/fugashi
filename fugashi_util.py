import os
import platform
import subprocess
import glob

def mecab_config(com="mecab-config"):
    output = subprocess.check_output([com, "--inc-dir", "--libs-only-L", "--libs-only-l"])
    if not isinstance(output, str):
        output = output.decode("utf-8")
    return output

def check_libmecab():
    if os.name == 'nt':
        win_mecab_dir = r'C:\mecab'
        return win_mecab_dir+"\n"+win_mecab_dir+"\nlibmecab\n", [("lib\\site-packages\\", ["{}\\libmecab.dll".format(win_bin_dir)])]

    try:
        output = mecab_config()
        return output, []
    except:
        pass

    os.makedirs("build/mecab", exist_ok=True)
    os.chdir("build/mecab")

    if platform.system().startswith("CYGWIN"):
        rep = "mecab-cygwin64" if platform.machine()=="x86_64" else "mecab-cygwin32"
        subprocess.run(["git", "clone", "--depth=1", "https://github.com/KoichiYasuoka/"+rep])
        os.chdir(rep)
        subprocess.run(["sh", "-x", "./install.sh", "/usr/local"])
        output = mecab_config("/usr/local/bin/mecab-config")
        return output, []

    try:
        subprocess.run(["apt-get", "install", "-y", "libmecab-dev"])
        output = mecab_config("mecab-config")
        return output, []
    except:
        pass

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
    src_dir="build/mecab/mecab/mecab/src"
    obj=" ".join(glob.glob(".libs/*.o")).replace(".libs/",src_dir+"/.libs/")
    return src_dir+"\n\nstdc++\n"+obj, []
