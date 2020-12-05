import streamlit as st

import fugashi

tagger = fugashi.Tagger()
st.set_page_config(page_title="fugashi demo")
st.title('fugashi demo')


"""
Input the text you'd like to analyze.
"""

text = st.text_area("input", "麩菓子は、麩を主材料とした日本の菓子。")

def make_row(word):
    ff = word.feature
    return dict(surface=word.surface, kana=ff.kana, lemma=ff.lemma, 
            pos1=ff.pos1, pos2=ff.pos2, pos3=ff.pos3, pos4=ff.pos4)


data = [make_row(ww) for ww in tagger(text)]

st.table(data)






