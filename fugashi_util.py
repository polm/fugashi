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
    try:
        output = mecab_config()
        return output
    except:
        pass

    try:
        subprocess.run(["apt-get", "install", "-y", "libmecab-dev"])
        output = mecab_config()
        return output
    except:
        pass

    os.makedirs("build/mecab", exist_ok=True)
    os.chdir("build/mecab")

    if platform.system().startswith("CYGWIN"):
        rep = "mecab-cygwin64" if platform.machine()=="x86_64" else "mecab-cygwin32"
        subprocess.run(["git", "clone", "--depth=1", "https://github.com/KoichiYasuoka/"+rep])
        output = mecab_config(rep+"/bin/mecab-config")
        return output.replace("/usr/local/", "build/mecab/"+rep+"/")
    try:
        subprocess.run(["apt-get", "download", "libmecab-dev", "libmecab2"])
        for deb in glob.glob("libmecab*.deb"):
            subprocess.run(["dpkg", "-x", deb, "."])
        output = mecab_config("usr/bin/mecab-config")
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
