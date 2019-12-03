# fugashi

![Fugashi by Irasutoya](fugashi.png)

Fugashi is a Cython wrapper for [MeCab](https://taku910.github.io/mecab/). It
doesn't attempt to cover all of the potential use cases of MeCab, instead
dealing with only the most common ones.

- Only UniDic is supported, you can't use IPADic. UniDic Neologd is fine.
- Only UTF-8 is supported.
- Only Python3 is supported.

## Usage

    from fugashi import Tagger

    tagger = Tagger('-Owakati')
    tagger.parse("麩菓子（ふがし）は、麩を主材料とした日本の菓子。")
    # => '麩 菓子 （ ふ が し ） は 、 麩 を 主材 料 と し た 日本 の 菓子 。 \n'
    for word in tagger.parseToNodeList("麩菓子（ふがし）は、麩を主材料とした日本の菓子。"):
        print(word, word.feature.lemma, word.pos, sep='\t')
        # "feature" is the Unidic feature data as a named tuple
