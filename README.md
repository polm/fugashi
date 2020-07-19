[![Current PyPI packages](https://badge.fury.io/py/fugashi.svg)](https://pypi.org/project/fugashi/)
![Test Status](https://github.com/polm/fugashi/workflows/test-manylinux/badge.svg)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/fugashi)](https://pypi.org/project/fugashi/)
![Supported Platforms](https://img.shields.io/badge/platforms-linux%20macosx%20windows-blue)

# fugashi

<img src="https://github.com/polm/fugashi/raw/master/fugashi.png" width=125 height=125 alt="Fugashi by Irasutoya" />

Fugashi is a Cython wrapper for [MeCab](https://taku910.github.io/mecab/), a
Japanese tokenizer and morphological analysis tool.  Wheels are provided for
Linux, OSX, and Win64, and UniDic is [easy to install](#installing-a-dictionary).

**issueを英語で書く必要はありません。**

See the [blog post](https://www.dampfkraft.com/nlp/fugashi.html) for background
on why Fugashi exists and some of the design decisions.

If you are on an unsupported platform (like PowerPC), you'll need to install
MeCab first. It's recommended you install [from
source](https://github.com/taku910/mecab).

## Usage

```python
from fugashi import Tagger

tagger = Tagger('-Owakati')
text = "麩菓子は、麩を主材料とした日本の菓子。"
tagger.parse(text)
# => '麩 菓子 は 、 麩 を 主材 料 と し た 日本 の 菓子 。'
for word in tagger(text):
    print(word, word.feature.lemma, word.pos, sep='\t')
    # "feature" is the Unidic feature data as a named tuple
```

## Installing a Dictionary

Fugashi requires a dictionary. [UniDic](https://unidic.ninjal.ac.jp/) is
recommended, and two easy-to-install versions are provided.

  - [unidic-lite](https://github.com/polm/unidic-lite), a 2013 version of Unidic that's relatively small
  - [unidic](https://github.com/polm/unidic-py), the latest UniDic 2.3.0, which is 1GB on disk and requires a separate download step

If you just want to make sure things work you can start with `unidic-lite`, but
for more serious processing `unidic` is recommended. For production use you'll
generally want to generate your own dictionary too; for details see the [MeCab
documentation](https://taku910.github.io/mecab/learn.html).

To get either of these dictionaries, you can install them directly using `pip`
or do the below:

```sh
pip install fugashi[unidic-lite]

# The full version of UniDic requires a separate download step
pip install fugashi[unidic]
python -m unidic download
```

## Dictionary Use

Fugashi is written with the assumption you'll use Unidic to process Japanese,
but it supports arbitrary dictionaries. 

If you're using a dictionary besides Unidic you can use the GenericTagger like this:

```python
from fugashi import GenericTagger
tagger = GenericTagger()

# parse can be used as normal
tagger.parse('something')
# features from the dictionary can be accessed by field numbers
for word in tagger(text):
    print(word.surface, word.feature[0])
```

You can also create a dictionary wrapper to get feature information as a named tuple. 

```python
from fugashi import GenericTagger, create_feature_wrapper
CustomFeatures = create_feature_wrapper('CustomFeatures', 'alpha beta gamma')
tagger = GenericTagger(wrapper=CustomFeatures)
for word in tagger.parseToNodeList(text):
    print(word.surface, word.feature.alpha)
```

## Alternatives

If you have a problem with Fugashi feel free to open an issue. However, there
are some cases where it might be better to use a different library.

- If you don't want to deal with installing MeCab at all, try [SudachiPy](https://github.com/WorksApplications/SudachiPy).
- If you need to work with Korean, try [KoNLPy](https://konlpy.org/en/latest/).

## License and Copyright Notice

Fugashi is released under the terms of the [MIT license](./LICENSE). Please
copy it far and wide.

Fugashi is a wrapper for MeCab, and Fugashi wheels include MeCab binaries.
MeCab is copyrighted free software by Taku Kudo `<taku@chasen.org>` and Nippon
Telegraph and Telephone Corporation, and is redistributed under the [BSD
License](./LICENSE.mecab).
