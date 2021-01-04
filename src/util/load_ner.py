import pandas as pd
import pymysql


class SentNER:
    def __init__(self, sent_list, attr_list):
        self.article_id = sent_list[1]
        self.sent_id = attr_list[0]
        self.cui1_dic = attr_list[1]
        self.cui2_dic = attr_list[2]
        self.title = sent_list[2]
        self.text = sent_list[3]
        self.article_structure = sent_list[4]

    def __str__(self):
        return "sent Id: " + str(self.sent_id) + "\n" + "NER cui1: " + str(self.cui1_dic) + "\n" +\
                 "NER cui2: " + str(self.cui2_dic) + "\n" + 'title: ' + str(self.title) + '\n' +\
                 'text: ' + str(self.text) + '\n' + 'article_structure: ' + str(self.article_structure)

    def __repr__(self):
        return "sent Id: " + str(self.sent_id) + "\n" + "NER cui1: " + str(self.cui1_dic) + "\n" +\
                 "NER cui2: " + str(self.cui2_dic) + "\n" + 'title: ' + str(self.title) + '\n' +\
                 'text: ' + str(self.text) + '\n' + 'article_structure: ' + str(self.article_structure)

class LoadNERs:
    def __init__(self, NER_filepath, sent_filepath=None):
        self.NER_filepath = NER_filepath
        self.sent_filepath = sent_filepath
        self.cui1_type = []
        self.cui2_type = []

    def get_type_list(self, type1, type2):
        self.cui1_type = type1
        self.cui2_type = type2

    def Process(self, sent_id, sent, NER_cui1, NER_cui2):
        NER_cui1_dic = {}  #{CUI:[start, end, entity, cui_type,is_title]}
        NER_cui2_dic = {}
        for NER in NER_cui1:
            if NER[6] not in NER_cui1_dic:
                NER_cui1_dic[NER[6]] = []
            NER_cui1_dic[NER[6]].append(NER[3:6] + NER[7:9]) 
        for NER in NER_cui2:
            if NER[6] not in NER_cui2_dic:
                NER_cui2_dic[NER[6]] = []
            NER_cui2_dic[NER[6]].append(NER[3:6] + NER[7:9])
        sent_list = sent.split('|')
        return SentNER(sent_list, [sent_id, NER_cui1_dic, NER_cui2_dic])
        
    """逐行读取文件并返回迭代器"""
    def Reader(self, num):
        NER_infile = open(self.NER_filepath)
        sent_infile = open(self.sent_filepath)

        i = 0
        NER_result = NER_infile.readline()
        NER_result_list = NER_result.strip().split('|')
        while NER_result.strip():
            if i ==num:
                break
            NER_cui1 = []  #[[article_id, sent_id, cui_id, start, end, entity, cui_type, is_title, is_article_structure], ...]
            NER_cui2 = []
            while NER_result_list[1] == str(i):
                if NER_result_list[-1] == '0':
                    if NER_result_list[-3] in self.cui1_type:
                        NER_cui1.append(NER_result_list)
                    if NER_result_list[-3] in self.cui2_type:
                        NER_cui2.append(NER_result_list)
                NER_result = NER_infile.readline()
                if not NER_result:
                    break
                else:
                    NER_result_list = NER_result.strip().split('|')
            sent = sent_infile.readline().lower()
            if NER_cui1 and NER_cui2:
                yield self.Process(i, sent, NER_cui1, NER_cui2)
            i += 1
        NER_infile.close()
        sent_infile.close()


def test():
    filepath = '../output/pubmed_NERresult_0.txt'
    sent_path = '../output/pubmed.txt0.txt'
    relation_path = '../data/diso_lab_relation.txt'
    relation_table = pd.read_table(relation_path,sep="|", header=None)
    type1 = list(set(relation_table.iloc[:,1].values))
    type2 = list(set(relation_table.iloc[:,4].values))
    print(type2)
    ner_loader = LoadNERs(filepath,sent_path)
    print('- loading NER...')
    ner_loader.get_type_list(type1,type2)
    reader = ner_loader.Reader(5)
    print('- done')
    for item in reader:
        print(item)


if __name__ == '__main__':
    test()
