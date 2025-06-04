#!/bin/bash
# Install mecab, then build wheels
set -e

# install MeCab
# TODO specify the commit used here
git clone --depth=1 https://github.com/taku910/mecab.git
cd mecab/mecab
if [ "$(uname -m)" == "aarch64" ]
then
    ./configure --enable-utf8-only --build=aarch64-unknown-linux-gnu
else
    ./configure --enable-utf8-only
fi
make
make install

# Hack
# see here:
# https://github.com/RalfG/python-wheels-manylinux-build/issues/26
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

# Build the wheels
Python="cp39-cp39 cp310-cp310 cp311-cp311 cp312-cp312 cp313-cp313"
for PYVER in $Python; do
  # build the wheels
  /opt/python/$PYVER/bin/pip wheel /github/workspace -w /github/workspace/wheels || { echo "Failed while buiding $PYVER wheel"; exit 1; }
done

# fix the wheels (bundles libs)
for wheel in /github/workspace/wheels/*.whl; do
  if [ "$(uname -m)" == "aarch64" ]
  then
    auditwheel repair "$wheel" --plat manylinux2014_aarch64 -w /github/workspace/manylinux-aarch64-wheels
  else
    auditwheel repair "$wheel" --plat manylinux2014_x86_64 -w /github/workspace/manylinux2014-wheels
  fi
done

echo "Built wheels:"
if [ "$(uname -m)" == "aarch64" ]
then
    ls /github/workspace/manylinux-aarch64-wheels
else
    ls /github/workspace/manylinux2014-wheels
fi
