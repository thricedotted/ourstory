import cPickle as pickle
from collections import Counter

#phrases = ["i was", "you were", "i am", "you are", "i will"]
phrases = ["i am", "you are"]

def sequence_index(ngram, words):
    for i, _ in enumerate(ngram.words):
        piece = ngram.words[i:i+len(words)]
        if words == piece:
            return i
    return -1

big_dict = {}

for phrase, ngrams in zip(phrases, boo):
    w1, w2 = phrase.split()

    if w1 not in big_dict:
        big_dict[w1] = {}

    if w2 not in big_dict[w1]:
        big_dict[w1][w2] = {}

    phrase_idxs = [sequence_index(ng, phrase.split()) for ng in ngrams]

    phrase_vb = [ng for p_idx, ng in zip(phrase_idxs, ngrams)
            #if ng[p_idx+1].head is not None
            #and ng[p_idx+1].head.postag.startswith('VB')
            if ng[p_idx+1].headposition > -1
            and ng[p_idx+1].headposition < len(ng)
            and ng[ng[p_idx+1].headposition].postag.startswith('JJ')
            and p_idx+2 < len(ng)]

    phrase_nn = [ng for p_idx, ng in zip(phrase_idxs, ngrams)
            #if ng[p_idx+1].head is not None
            #and ng[p_idx+1].head.postag.startswith('NN')
            if ng[p_idx+1].headposition > -1
            and ng[p_idx+1].headposition < len(ng)
            and ng[ng[p_idx+1].headposition].postag.startswith('JJ')
            and p_idx+2 < len(ng)]

    phrase_jj = [ng for p_idx, ng in zip(phrase_idxs, ngrams)
            #if ng[p_idx+1].head is not None
            if ng[p_idx+1].headposition > -1
            and ng[p_idx+1].headposition < len(ng)
            and ng[ng[p_idx+1].headposition].postag.startswith('JJ')
            and p_idx+2 < len(ng)]

    big_dict[w1][w2]['VB'] = Counter(t.surface for ng in phrase_vb for t in ng if t.postag.startswith('VB'))
    big_dict[w1][w2]['NN'] = Counter(t.surface for ng in phrase_nn for t in ng if t.postag.startswith('NN'))
    big_dict[w1][w2]['JJ'] = Counter(t.surface for ng in phrase_jj for t in ng if t.postag.startswith('JJ'))
