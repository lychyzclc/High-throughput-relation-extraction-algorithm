import pickle

import pymysql


class LoadCuiEmbedding:
    def __init__(self, savepath):
        self.embed_dic = {}
        self.savepath = savepath

    def build(self):
        db = pymysql.connect(host = '127.0.0.1', user = 'root', password = '')
        cur = db.cursor()
        cur.execute('use CUI2embed_par;')
        cur.execute('select * from cui2embed;')
        results = cur.fetchall()
        for r in results:
            self.embed_dic[r[0]] = r[1]
        self.save()

    def save(self):
        print("saving")
        f = open(self.savepath,"wb")
        pickle.dump(self.embed_dic,f)
        f.close()

    def load(self):
        print("loading")
        f = open(self.savepath,"rb")
        self.embed_dic = pickle.load(f)
        f.close()

    def get_embed(self, cui):
        if cui in self.embed_dic:
            return self.embed_dic[cui]
        else:
            return self.embed_dic['empty']


def test():
    savepath = "../src/trie.pkl"
    embed_loader = LoadCuiEmbedding(savepath)
    embed_loader.build()
    embed_loader.save()

if __name__ == '__main__':
    test()
