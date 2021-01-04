import pickle
import re

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


"""Trie匹配后的结果"""


class TrieMatchResult:
    def __init__(self, begin, end, phrase, phrase_attr):
        self.begin = begin
        self.end = end
        self.phrase = phrase
        self.phrase_attr = phrase_attr

    def __str__(self):
        return "phrase begin: "+str(self.begin)+"\nphrase end: "+str(self.end)+\
        "\nphrase: "+str(self.phrase)+"\nphrase_attr:"+str(self.phrase_attr)

    def __repr__(self):
        return "phrase begin: "+str(self.begin)+"\nphrase end: "+str(self.end)+\
        "\nphrase: "+str(self.phrase)+"\nphrase_attr:"+str(self.phrase_attr)


class Trie:
    def __init__(self, phrase_set_path, save_path, load_path):
        self.root = TrieNode()
        self.phrase_set_path = phrase_set_path
        self.save_path = save_path
        self.load_path = load_path

    def insertPhrase(self, phrase, phrase_attr):
        node = self.root
        words = phrase.split()

        for ch in phrase:
            if ch not in node.table:
                node.table[ch] = TrieNode()
            node = node.table[ch]

        node.phrase_end = True
        node.phrase = phrase
        node.phrase_attr = phrase_attr

    # if text[start:] has a prefix in this trie
    # return the end position of this match
    # else return -1
    def search(self, text, start=0):
        node = self.root
        if start != 0:
            if not (re.match("[a-zA-z0-9]",text[start]) and\
                 re.match("[^a-zA-z0-9]",text[start-1])):
                return -1, node.phrase, node.phrase_attr
        tmp_result = (-1, None, None)
        for i in range(start, len(text)):
            if node.phrase_end:
                if re.match("[a-zA-z0-9]",text[i-1]) and\
                 re.match("[^a-zA-z0-9]",text[i]):
                    tmp_result = i, node.phrase, node.phrase_attr
            if text[i] not in node.table:
                break
            node = node.table[text[i]]
        return tmp_result

    """建Trie树"""

    def build(self):
        f = open(self.phrase_set_path, "rb")
        term_list = pickle.load(f)
        for term, cui, cui_type in tqdm(term_list):
            phrase = term.lower()
            phrase_attr = [cui, cui_type]
            self.insertPhrase(phrase, phrase_attr)
        self.save()

    def save(self):
        print("saving")
        f = open(self.save_path, "wb")
        pickle.dump(self.root, f)
        f.close()

    def load(self):
        print("loading")
        f = open(self.load_path, "rb")
        self.root = pickle.load(f)
        f.close()

    """匹配文本"""

    def match(self, text):
        text = text.strip().lower() + ' '
        result_list = []
        for i in range(len(text)):
            res = self.search(text, i)
            if res[0] > 0:
                result_item = TrieMatchResult(i, res[0], res[1], res[2])
                result_list.append(result_item)
        return result_list


def test():
    phrase_set_path = "terms.pkl"
    save_path = "trie.pkl"
    load_path = "trie.pkl"
    trie = Trie(phrase_set_path, save_path, load_path)
    trie.load()

    text = "Autism"
    print(trie.match(text))


if __name__ == "__main__":
    test()
