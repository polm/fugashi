import fugashi

tagger = fugashi.Tagger()
sample_string = 'そうですねであのーちょうど歌を歌い始めて色んなコピーバンドとかをやってた時に後ろでドラムを叩いてくれてたのがドラムのちゃんまつだったんですよ'

candidate_paths = tagger.nbest(sample_string, 5)
for path in candidate_paths:
    print([f'{w.feature.lemma}' for w in path])
    
for path in candidate_paths:
    print(path)