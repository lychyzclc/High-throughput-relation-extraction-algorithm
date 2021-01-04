import pickle
import re
from collections import defaultdict

import pandas as pd
from tqdm import tqdm

"""Trie结点类"""
class TrieNode:
    def __init__(self):
        self.table = dict()
        self.phrase_end = False
        self.phrase = None
        self.phrase_attr = None

    def __len__(self):
        return len(self.table)


class Trie:
    def __init__(self,save_path,load_path):
        self.root = TrieNode()
        self.save_path = save_path
        self.load_path = load_path

    def insertPhrase(self, phrase,phrase_attr):
        node = self.root
        words = phrase.split()

        for ch in phrase:
            if ch not in node.table:
                node.table[ch] = TrieNode()
            node = node.table[ch]

        node.phrase_end = True
        node.phrase = phrase
        node.phrase_attr = phrase_attr

    def search(self, cui1_dic, cui2_dic, start=0):
        result = []
        for cui1 in cui1_dic:
            node = self.root
            for i in range(len(cui1)):
                if cui1[i] not in node.table:
                    break
                node = node.table[cui1[i]]
            if node.phrase_end:
                for cui2 in cui2_dic:
                    if cui2 in node.phrase_attr:
                        result.append([cui1, cui2])
        return result

    def search_notin(self, cui1_dic, cui2_dic, start=0):
        result = []
        for cui1 in cui1_dic:
            node = self.root
            for i in range(len(cui1)):
                if cui1[i] not in node.table:
                    for cui2 in cui2_dic:
                        result.append([cui1, cui2])
                    break
                node = node.table[cui1[i]]
            if node.phrase_end:
                for cui2 in cui2_dic:
                    if cui2 not in node.phrase_attr:
                        result.append([cui1, cui2])
        return result

    """建Trie树"""
    def build(self, relation_path):
        relations = pd.read_table(relation_path, sep="|", header=None)
        cui_pair_dict = defaultdict(list)
        for cui1, cui2 in relations.iloc[:,[0,3]].values:
            cui_pair_dict[cui1].append(cui2)

        for j, (cui1, cui2s) in enumerate(cui_pair_dict.items()):
            if j%1000 == 0:
                print('%d finished'%j)
            self.insertPhrase(cui1, cui2s)
        self.save()

    def save(self):
        f = open(self.save_path,"wb")
        pickle.dump(self.root,f)
        f.close()


    def load(self):
        f = open(self.load_path,"rb")
        self.root = pickle.load(f)
        f.close()

def test(build=True):
    trie = Trie('../../data/trie_diso_lab.pkl','../../data/trie_diso_lab.pkl')
    if build:
        trie.build('../../data/diso_lab_relation.txt')
    trie.load()
    print(trie.search(["C0201975","C0042014"],["C1962972", "C1962972"]))


if __name__ == '__main__':
    test()
