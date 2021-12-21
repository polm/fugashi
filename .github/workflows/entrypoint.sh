#!/bin/bash
# Install mecab, then build wheels
set -e

cd /github/workspace

# Install mecab
git clone --depth=1 git://github.com/taku910/mecab.git
cd mecab/mecab
if [ "$(uname -m)" == "aarch64" ]
then
    ./configure --enable-utf8-only --build=aarch64-unknown-linux-gnu --prefix=/github/workspace/mecab-out
else
    ./configure --enable-utf8-only --prefix=/github/workspace/mecab-out
fi
make
make install

cd /github/workspace

# Install dependencies
/opt/python/$1/bin/pip install -r requirements.txt

# Build PyExt
export PATH=$PATH:/github/workspace/mecab-out/bin

/opt/python/$1/bin/python setup.py build

# Prepare for upload
mkdir -p upload/
mv build/lib.*/fugashi/* upload/
cp mecab-out/lib/libmecab.so.2.0.0 "upload/libmecab.$(uname -m).so"

# Patchelf time!
patchelf --set-rpath '$ORIGIN/' upload/fugashi.*.so
patchelf --replace-needed libmecab.so.2 "libmecab.$(uname -m).so" upload/fugashi.*.so
