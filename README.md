# fugashi

<img src="https://github.com/polm/fugashi/raw/master/fugashi.png" width=125 height=125 alt="Fugashi by Irasutoya" />

Fugashi is a Cython wrapper for [MeCab](https://taku910.github.io/mecab/). It
doesn't attempt to cover all of the potential use cases of MeCab, instead
dealing with only the most common ones.

- Only UniDic is supported, you can't use IPADic. UniDic Neologd is fine.
- Only UTF-8 is supported.
- Only Python3 is supported.

See the [blog post](https://www.dampfkraft.com/nlp/fugashi.html) for background
on why Fugashi exists and some of the design decisions.

## Usage

    from fugashi import Tagger

    tagger = Tagger('-Owakati')
    text = "麩菓子（ふがし）は、麩を主材料とした日本の菓子。"
    tagger.parse(text)
    # => '麩 菓子 （ ふ が し ） は 、 麩 を 主材 料 と し た 日本 の 菓子 。'
    for word in tagger.parseToNodeList(text):
        print(word, word.feature.lemma, word.pos, sep='\t')
        # "feature" is the Unidic feature data as a named tuple

## Alternatives

If you have a problem with Fugashi feel free to open an issue. However, there
are some cases where it might be better to use a different library.

- If you want to use MeCab but don't have a C compiler, use [natto-py](https://github.com/buruzaemon/natto-py).
- If you don't want to deal with installing MeCab at all, try [SudachiPy](https://github.com/WorksApplications/SudachiPy).

Note that these are both slower than Fugashi according to a [benchmark I
wrote](https://github.com/polm/ja-tokenizer-benchmark). 
