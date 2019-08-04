import numpy as np
import networkx as nx
import jieba
import re


class KeyWord:
    def __init__(self, win_size=10, words=20):
        self.news = None
        self.win_size = win_size
        self.words = words
        self.stopwords = []
        try:
            with open('stopword.txt', 'r') as f:
                self.stopwords = f.read().splitlines()
        except:
            print("stopword.txt not exist")
            self.stopwords = []
    
    def __build_graph(self, tokens):
        graph = {}
        _m = len(tokens)

        for i in range(_m):
            left = i - self.win_size
            right = i + self.win_size
            if left < 0: left = 0
            if right > _m: right = _m
            
            graph[tokens[i]] = tokens[left:i]
            graph[tokens[i]] += tokens[i:right]

        g = nx.DiGraph(graph)

        pr = nx.pagerank(g)
        
        return pr
    
    def build_tokens(self, news):
        clean_news = ' '.join(re.findall(re.compile('[\w|\d]+'), news))
        
        tokens = ' '.join(jieba.cut(clean_news)).split()
        
        tokens = [t for t in tokens if t not in self.stopwords]
        
        return tokens
    
    def extract(self, news):
        
        tokens = self.build_tokens(news)
        
        pr = self.__build_graph(tokens)

        pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)

        return [_pr[0] for _pr in pr][:self.words]