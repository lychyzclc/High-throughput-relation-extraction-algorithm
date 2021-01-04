import argparse
import json
import logging

from tqdm import tqdm

from util.load_raw_sentence import LoadSentences, Sentence
from util.load_type_list import LoadTypelist
from util.logger import get_logger

logger = logging.getLogger(__name__)


class Cleaner:
    def __init__(self, sentence_path, type_path, save_path, exception_path):
        self.sentence_path = sentence_path
        self.type_path = type_path
        self.save_path = save_path
        self.exception_path = exception_path
        self.sentence_list = []

    def init(self):
        sentloader = LoadSentences(self.sentence_path)
        typeloader = LoadTypelist(self.type_path)
        logger.info('- loading sentence...')
        self.reader = sentloader.Reader()
        logger.info('- done')
        logger.info('- loading type list...')
        self.type_dic = typeloader.Load()
        logger.info('- done')

    def Process(self):
        with open(self.save_path, 'w') as outfile:
            with open(self.exception_path, 'w') as exception_file:
                for sentence in tqdm(self.reader):
                    if sentence.is_proper_sentence:
                        if sentence.entity_in_sent:
                            mask1 = self.type_dic[sentence.type1]
                            mask2 = self.type_dic[sentence.type2]
                            sentence.mask([mask1, mask2])
                            sentence.calculate_pos()
                            outfile.writelines(str(sentence))
                    else:
                        exception_file.writelines(sentence.text + '\n')


def general_clean(sentence_path, type_path, save_path, exception_path):
    cleaner = Cleaner(sentence_path, type_path, save_path, exception_path)
    cleaner.init()
    cleaner.Process()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type_path',
                        action='store',
                        type=str,
                        help='The path to load cui types')
    parser.add_argument('--input_file',
                        action='store',
                        type=str,
                        help='The path to load sentences')
    parser.add_argument('--output_file',
                        action='store',
                        type=str,
                        help='The path to save general clean result')
    parser.add_argument('--error_file',
                        action='store',
                        type=str,
                        help='The path to output exception')
    parser.add_argument('--log_file',
                        action='store',
                        type=str,
                        help='The path to output exception')

    args = parser.parse_args()

    logger = get_logger(logger, args.log_file)

    general_clean(args.input_file, args.type_path, args.output_file,
                  args.error_file)
