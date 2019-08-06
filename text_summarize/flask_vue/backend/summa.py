from gensim.models import Word2Vec
import re
import jieba
import numpy as np
import pandas as pd
from scipy.sparse import linalg 
from scipy.spatial.distance import cosine
from collections import Counter

class SenVec:
    def __init__(self, alpha=0.0001):
        self.alpha = alpha
        self.model, self.norm_vector = self.__load_vector()
        self.counter, self.sum_words = self.__load_prob()
        self.sens = None
        self.stopwords = self.__load_stopwords()
        
    def __load_stopwords(self):
        stopwords = []
        try:
            with open('stopword.txt', 'r') as f:
                stopwords = f.read().splitlines()
        except:
            print("stopword.txt not exist")
            stopwords = []
            
        return stopwords

    
    def __load_vector(self):
        try:
            model = Word2Vec.load("vector")
            words_dict = dict({})
            for idx, key in enumerate(model.wv.vocab):
                words_dict[key] = model.wv[key]
            
            all_embs = np.stack(words_dict.values())
            vector_size = all_embs.shape[1]
            
            emb_mean,emb_std = all_embs.mean(), all_embs.std()
            
            norm_vector = np.random.normal(emb_mean, emb_std, (1, vector_size))   
        except:
            print("error when load vector model")
            model = None
            norm_vector = None
            
        return model, norm_vector
    
    def __word_vector(self, word):
        try:
            return self.mode.wv[word]
        except:
            return self.norm_vector
    
    def __load_prob(self):
        try:
            with open('counter.txt', 'r') as f:
                lines = [line.strip().split(':') for line in f]

            counter = Counter({line[0]: int(line[1]) for line in lines})

            with open('sum_count.txt', 'r') as f:
                sum_words = int(f.read())
        except:
            print("error when load prob")
            counter = None
            sum_words = 1
    
        return counter, sum_words
    
    def __word_prob(self, word):
        if word in self.counter:
            return self.counter[word] / self.sum_words
        else:
            return 1 / self.sum_words
    
    def __cut_to_sen(self, sentences):
        marks = "，|。|？|！|；|：|,|\.|!|\?|:|\""
        sens = [sen for sen in re.split(marks, sentences) if sen]
        return sens
    
        
    def __cut_to_tokens(self, sen):
        clean_sen = ' '.join(re.findall(re.compile('[\w|\d]+'), sen))
        
        tokens = ' '.join(jieba.cut(clean_sen)).split()
        
        tokens = [t for t in tokens if t not in self.stopwords]
        
        return tokens

    def __calc(self, word):
        return self.alpha / (self.alpha + self.__word_prob(word)) * self.__word_vector(word)
    
    def __vector(self, sens):
        sen_vec = []
        for sen in sens:
            if not sen: continue
                
            words = self.__cut_to_tokens(sen)
            
            vector_s = [self.__calc(word) for word in words if word]
                
            vector_s = 1 / len(words) * sum(vector_s)
            
            sen_vec.append(vector_s)

        #if not define v0, u will be random
        _sen_vec = np.array(sen_vec).reshape(len(sen_vec), -1).T
        v0 = np.ones(min(_sen_vec.shape))
        u, s, v = linalg.svds(_sen_vec, k=1, v0=v0)
        #u = np.around(u, decimals=12)

        res = []
        for vec in sen_vec:
            res.append(vec.T - np.dot(np.dot(u, u.T), vec.T))

        return res
    
    def cosine(self, vec1, vec2):
        return 1 - cosine(vec1, vec2)
    
    def get_sens(self):
        return self.sens 
    
    def get_vector(self, sentences):
        self.sens = self.__cut_to_sen(sentences)

        return self.__vector(self.sens)

    def pangrank(self, matrix, eps = 1.0e-8, d = 0.85):

        n = matrix.shape[0]
        R = np.ones((n, 1)) * 1 / n
        new_R = np.zeros((n, 1))
        E = np.ones((n, n))

        while True:
            new_R = ((1 - d) / n * E + d * matrix.T).dot(R)
            if np.linalg.norm(new_R - R) <= eps:
                break
            else:
                R = new_R

        return new_R    
    
    def textrank(self, sentences):
        sen_vec = self.get_vector(sentences)

        n = len(sen_vec)
        S = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j: continue
                
                S[i][j] = self.cosine(sen_vec[i], sen_vec[j])
        
        for i in range(n):
            S[i] /= S[i].sum()
        
        return self.pangrank(S)
    
    def summarization(self, sentences, count=5):
        sens = self.__cut_to_sen(sentences)
        rank = self.textrank(sentences)
        
        rank = dict(zip(sens, rank))

        rank = sorted(rank.items(), key=lambda x: x[1], reverse=True)
        #print(rank)
        return [r[0] for r in rank]
