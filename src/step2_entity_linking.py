import argparse
import logging
import os
from multiprocessing import Process

from tqdm import tqdm

from util.load_sentence import LoadSentences
from util.logger import get_logger
from util.trie import Trie, TrieMatchResult, TrieNode

logger = logging.getLogger(__name__)


class NERresult:
    def __init__(self, art_id, sen_id, NER_id, trie_match_result, is_title,
                 is_structure):
        self.article_id = art_id
        self.sen_id = sen_id
        self.NER_id = NER_id
        self.begin = trie_match_result.begin
        self.end = trie_match_result.end
        self.term = trie_match_result.phrase
        self.cui = trie_match_result.phrase_attr[0]
        self.cui_type = trie_match_result.phrase_attr[1]
        self.is_title = is_title
        self.is_structure = is_structure

    def __str__(self):
        return str(self.article_id)+'|'+str(self.sen_id)+'|'+str(self.NER_id)+'|'+str(self.begin)+\
            '|'+str(self.end)+'|'+str(self.term)+'|'+str(self.cui)+'|'+str(self.cui_type)+'|'\
            +str(self.is_title)+'|'+str(self.is_structure)  +'\n'

    def tolist(self):
        return[self.article_id,self.sen_id,self.NER_id,self.begin,self.end,self.term,\
                self.cui,self.cui_type,self.is_title,self.is_structure]


class GenerateNER:
    def __init__(self, sentences_path, result_path, trie):
        self.sentences_num = -1
        self.sentences_path = sentences_path
        self.result_path = result_path
        self.trie = trie
        self.reader = None

    def init(self):
        logger.info("- init begin...")
        logger.info("- loading sentences...")
        sentences = LoadSentences(self.sentences_path, self.sentences_num)
        logger.info("- done")
        self.reader = sentences.Reader()
        return

    def process(self):
        with open(self.result_path, "w") as f:
            sent_id = 0
            for each in tqdm(self.reader):

                result = self.trie.match(each.title)
                if result:
                    for NER_id in range(len(result)):
                        res_item = NERresult(each.article_id, sent_id, NER_id,
                                             result[NER_id], 1, 0)
                        f.write(str(res_item))

                result = self.trie.match(each.sentence)
                if result:
                    for NER_id in range(len(result)):
                        res_item = NERresult(each.article_id, sent_id, NER_id,
                                             result[NER_id], 0, 0)
                        f.write(str(res_item))

                result = self.trie.match(each.article_structure)
                if result:
                    for NER_id in range(len(result)):
                        res_item = NERresult(each.article_id, sent_id, NER_id,
                                             result[NER_id], 0, 1)
                        f.write(str(res_item))

                sent_id += 1
        logger.info("done")
        return


def generateNER(input_file, output_file, file_index, trie):
    input_file = input_file + str(file_index) + ".txt"
    output_file = output_file + str(file_index) + ".txt"
    generator = GenerateNER(input_file, output_file, trie)
    generator.init()
    generator.process()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file',
                        type=str,
                        help='The path to input file')
    parser.add_argument('--output_file',
                        type=str,
                        help='The path to output file')
    parser.add_argument('--data_dir',
                        type=str,
                        help='The path to output error')
    parser.add_argument('--terms_file',
                        type=str,
                        help='The path to output log')
    parser.add_argument('--trie_file', type=str, help='The path to output log')
    parser.add_argument('--log_file', type=str, help='The path to output log')
    parser.add_argument('--proc',
                        default=None,
                        type=int,
                        help='process number for multiprocess')

    args = parser.parse_args()

    logger = get_logger(logger, args.log_file)

    logger.info("- loading trie...")
    phrase_set_path = os.path.join(args.data_dir, args.terms_file)
    save_path = os.path.join(args.data_dir, args.trie_file)
    load_path = os.path.join(args.data_dir, args.trie_file)
    trie = Trie(phrase_set_path, save_path, load_path)
    trie.load()
    logger.info("- done")
    plist = []
    for i in range(args.proc):
        p = Process(target=generateNER,
                    args=(args.input_file, args.output_file, i, trie))
        p.start()
    for ap in plist:
        ap.join()
