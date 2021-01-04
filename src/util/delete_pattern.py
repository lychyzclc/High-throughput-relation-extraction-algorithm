import argparse
import re

from tqdm import tqdm

from load_general_clean_sentence import LoadSentences, Sentence


class DeletePattern:
    def __init__(self, infile, outfile, deletefile, pattern_same):
        self.sentence_loader = LoadSentences(infile)
        self.reader = self.sentence_loader.Reader()
        self.infile = infile
        self.outfile = outfile
        self.deletefile = deletefile
        self.pattern_same = pattern_same

    def process(self):
        cnt = 0
        with open(self.outfile, 'w') as of:
            with open(self.deletefile, 'w') as df:
                for sentence in tqdm(self.reader):
                    text = sentence.text
                    if self.pattern_same.search(text):
                        df.writelines(str(sentence))
                        cnt += 1
                    else:
                        of.writelines(str(sentence))
        return cnt

# delete t049 t033 t050 t019
class DeleteSpecificType:
    def __init__(self, infile, outfile, deletefile, delete_list):
        self.sentence_loader = LoadSentences(infile)
        self.reader = self.sentence_loader.Reader()
        self.infile = infile
        self.outfile = outfile
        self.deletefile = deletefile
        self.delete_list = delete_list

    def should_delete(self, text):
        for mask in self.delete_list:
            pattern = ' ' + mask + ' '
            if pattern in text:
                return True
        return False

    def process(self):
        cnt = 0
        with open(self.outfile, 'w') as of:
            with open(self.deletefile, 'w') as df:
                for sentence in tqdm(self.reader):
                    text = sentence.text
                    if self.should_delete(text):
                        df.writelines(str(sentence))
                        cnt += 1
                    else:
                        of.writelines(str(sentence))
        return cnt
