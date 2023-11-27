from konlpy.tag import Kkma
from konlpy.tag import Twitter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import csv
import pandas as pd

#file = r'C:\Users\ParkJinoh\Desktop\Crowlling\NaverNews_지진.csv'
#file = file.replace('\\','//')
news_content = []
#news = pd.read_csv(file,encoding='UTF8')

#for i in range(len(news['content'])):
#    news_content.append(news['content'][i])

kkma = Kkma()

tfidf = TfidfVectorizer()
cnt_vec = CountVectorizer()
graph_sentence = []
sentences = ''

twitter = Twitter()

stopwords = ["머니투데이","연합뉴스","데일리","동아일보","중앙일보","이데일리","조선일보","기자","아","휴","아이구","아이쿠","아이고","어","나","우리","저희","따라","의해","을","를","에","의","가"]


def text2sentence(text):
    sentence = kkma.sentences(text)
    for idx in range(0, len(sentence)):
        if len(sentence[idx]) <= 10:
            sentence[idx-1] += (' ' + sentence[idx])
            sentence[idx] = ''
    return sentence


def get_nouns(sentences):
    nouns = []
    for sentence in sentences:
        if sentence != '':
            nouns.append (' '.join([noun for noun in twitter.nouns(str(sentence))
                                    if noun not in stopwords and len(noun) > 1]))
    return nouns




def build_sent_graph(sentence):
    tfidf_mat = tfidf.fit_transform(sentence).toarray()
    graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
    return graph_sentence



def build_words_graph(sentence):
    cnt_vec_matt = normalize(cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
    vocab = cnt_vec.vocabulary_
    return np.dot(cnt_vec_matt.T, cnt_vec_matt), {vocab[word] : word for word in vocab}



def get_ranks(graph, d=0.85):
    A = graph
    matrix_size = A.shape[0]
    for id in range(matrix_size):
        A[id, id] = 0
        link_sum = np.sum(A[:,id])
        if link_sum != 0:
            A[:, id] /= link_sum
        A[:, id] *= -d
        A[id, id] = 1

    B = (1-d) * np.ones((matrix_size, 1))
    ranks = np.linalg.solve(A,B)
    return {idx: r[0] for idx, r in enumerate(ranks)}



def summarize(sent_num=5):
    sentences = text2sentence(news_content[-1])
    nouns = get_nouns(sentences)
    sent_graph = build_sent_graph(nouns)
    words_graph, idx2word = build_words_graph(nouns)
    sent_rank_idx = get_ranks(sent_graph)
    sent_rank_idx

    sorted_sent_rank_idx = sorted(sent_rank_idx, key=lambda k: sent_rank_idx[k], reverse=True)

    word_rank_idx = get_ranks(words_graph)
    sorted_word_rank_idx = sorted(word_rank_idx, key=lambda k: word_rank_idx[k], reverse=True)
    summary = []
    index = []
    for idx in sorted_sent_rank_idx[:sent_num]:
        index.append(idx)

    index.sort()

    for idx in index:
        summary.append(sentences[idx])

    for text in summary:
        print(text)
        print("\n")
    print("---------------------------------------------------")


    return ''.join(summary)

