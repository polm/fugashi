import os
import platform
import subprocess
import glob

def check_libmecab():
    try:
        output = subprocess.check_output(["mecab-config", "--inc-dir", "--libs-only-L", "--libs-only-l"])
        if not isinstance(output, str):
            output = output.decode("utf-8")
        return output
    except:
        pass

    os.makedirs("build/mecab", exist_ok=True)
    os.chdir("build/mecab")

    try:
        subprocess.run(["apt-get", "download", "libmecab-dev", "libmecab2"])
        for deb in glob.glob("libmecab*.deb"):
            subprocess.run(["dpkg", "-x", deb, "."])
        output = subprocess.check_output(["./usr/bin/mecab-config", "--inc-dir", "--libs-only-L", "--libs-only-l"])
        if not isinstance(output, str):
            output = output.decode("utf-8")
        return output.replace("/usr/","build/mecab/usr/")
    except:
        pass

    subprocess.run(["git", "clone", "--depth=1", "https://github.com/taku910/mecab"])
    os.chdir("mecab/mecab")
    if not os.path.isfile("mecab-config"):
        for f in ["aclocal.m4", "config.h.in", "configure", "Makefile.in", "src/Makefile.in"]:
            subprocess.run(["touch", f])
            subprocess.run(["sleep", "1"])
        subprocess.run(["./configure", "--enable-static", "--enable-shared", "--with-charset=utf8"])
    os.chdir("src")
    subprocess.run(["make", "libmecab.la"])
    if not os.path.isfile("libmecab.a"):
        os.symlink(".libs/libmecab.a", "libmecab.a")
    if not os.path.isfile("libmecab.so"):
        os.symlink(".libs/libmecab.so", "libmecab.so")
    return "build/mecab/mecab/mecab/src\nbuild/mecab/mecab/mecab/src\nmecab stdc++"
