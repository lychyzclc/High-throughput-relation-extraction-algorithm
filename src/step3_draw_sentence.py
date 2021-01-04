import argparse
import logging
import os
import signal
from multiprocessing import Process

import pandas as pd

from util.load_ner import LoadNERs
from util.logger import get_logger
from util.trie_entity_pair import Trie, TrieNode

logger = logging.getLogger(__name__)


def term(sig_num, addition):
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)


signal.signal(signal.SIGTERM, term)


class TitleSent:
    def __init__(self):
        self.titles = {}

    def insert(self, title, entities):
        if title in self.titles:
            if entities in self.titles[title]:
                return False
            else:
                self.titles[title].append(entities)
        else:
            self.titles[title] = [entities]
        return True


class EntityPair:
    def __init__(self, article_id, sent_id, title, text, article_structure,
                 cui1, cui2, cui1_attr, cui2_attr, title_sent):
        self.article_id = article_id
        self.sent_id = sent_id
        self.begin1 = cui1_attr[0]
        self.end1 = cui1_attr[1]
        self.cui1 = cui1
        self.entity1 = cui1_attr[2]
        self.cui1_type = cui1_attr[3]
        self.is_title1 = int(cui1_attr[4])
        self.begin2 = cui2_attr[0]
        self.end2 = cui2_attr[1]
        self.cui2 = cui2
        self.entity2 = cui2_attr[2]
        self.cui2_type = cui2_attr[3]
        self.is_title2 = int(cui2_attr[4])
        if self.is_title1 and self.is_title2:
            self.text = title
            self.title = '<EMPTY_TITLE>'
            self.article_structure = ' . . . '
            if title_sent.insert(title, [self.entity1, self.entity2]):
                self.is_entitypair = 1
            else:
                self.is_entitypair = 0
        elif (self.is_title1 and title == self.entity1) or \
            (self.is_title2 and title == self.entity2) or \
            (not self.is_title1 and not self.is_title2):
            self.title = title
            self.text = text
            self.article_structure = article_structure
            self.is_entitypair = 1
        else:
            self.is_entitypair = 0

    def __str__(self):
        return str(self.article_id)+'|' +str(self.sent_id)+'|' + str(self.title)+'|'+str(self.text)+'|'+str(self.article_structure)+\
            '|'+str(self.begin1)+'|'+str(self.end1)+'|'+str(self.entity1)+'|'+str(self.cui1)+'|'\
            +str(self.cui1_type)+'|'+str(self.is_title1)+'|'+str(self.begin2)+'|'+str(self.end2)+'|'\
            +str(self.entity2)+'|'+str(self.cui2)+'|'+str(self.cui2_type)+'|'+str(self.is_title2)  +'\n'


class GenerateEntityPair:
    def __init__(self, trie, relation_path, NER_path,
                 sent_path, result_path):
        self.relation_path = relation_path
        self.NER_path = NER_path
        self.sent_path = sent_path
        self.result_path = result_path
        self.trie = trie
        self.reader = None
        self.title_as_sent = TitleSent()

    def init(self):
        logger.info("- init begin")
        logger.info("- loading relations")
        relation_table = pd.read_table(self.relation_path,
                                       sep="|",
                                       header=None)
        type1 = list(set(relation_table.iloc[:, 1].values))
        type2 = list(set(relation_table.iloc[:, 4].values))
        logger.info("- loading NERs...")
        NERs = LoadNERs(self.NER_path, self.sent_path)
        NERs.get_type_list(type1, type2)
        self.reader = NERs.Reader(-1)
        logger.info("- done")

    def process(self):
        with open(self.result_path, "w") as f:
            sent_id = 0
            for idx, each in enumerate(self.reader):
                if idx % 10000 == 0:
                    logger.info("processing number: %d" % idx)
                result = self.trie.search(each.cui1_dic, each.cui2_dic)
                if result:
                    for cui1, cui2 in result:
                        cui1_attrs = each.cui1_dic[cui1]
                        cui2_attrs = each.cui2_dic[cui2]
                        for cui1_attr in cui1_attrs:
                            for cui2_attr in cui2_attrs:
                                item = EntityPair(each.article_id, each.sent_id, each.title, each.text, each.article_structure,\
                                     cui1, cui2, cui1_attr, cui2_attr, self.title_as_sent)
                                if item.is_entitypair:
                                    f.write(str(item))


def generateEntityPair(trie, relation_path, NER_file,
                       sent_file, output_file, file_index):
    NER_file_tmp = NER_file + str(file_index) + ".txt"
    sent_file_tmp = sent_file + str(file_index) + '.txt'
    output_file_tmp = output_file + str(file_index) + ".txt"
    generator = GenerateEntityPair(
            trie, relation_path, NER_file_tmp, 
            sent_file_tmp,output_file_tmp)
    generator.init()
    logger.info('processing...')
    generator.process()
    logger.info("- done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--relation_path',
                        action='store',
                        type=str,
                        help='The path to triplet file')
    parser.add_argument('--save_path',
                        action='store',
                        type=str,
                        help='The path to save trie_ep')
    parser.add_argument('--NER_file',
                        action='store',
                        type=str,
                        help='The path to input NER')
    parser.add_argument('--sent_file',
                        action='store',
                        type=str,
                        help='The path to input sentences')
    parser.add_argument('--output_file',
                        action='store',
                        type=str,
                        help='The path to output file')
    parser.add_argument('--log_file',
                        action='store',
                        type=str,
                        help='The path to log file')
    parser.add_argument('--proc',
                        action='store',
                        type=int,
                        help='num of sentence files to process')

    args = parser.parse_args()

    logger = get_logger(logger, args.log_file)

    trie = Trie(args.save_path, args.save_path)
    logger.info("- loading trie...")
    if not os.path.exists(args.save_path):
        logger.info("from %s building trie" % args.relation_path)
        trie.build(args.relation_path)
    else:
        trie.load()
    logger.info("- done")

    plist = []
    for i in range(args.proc):
        p = Process(target=generateEntityPair, args=(trie, args.relation_path,\
            args.NER_file, args.sent_file, args.output_file, i,))
        p.daemon = True
        p.start()
        plist.append(p)
    for ap in plist:
        ap.join()
