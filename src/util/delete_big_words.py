import argparse
import re

from tqdm import tqdm

from load_general_clean_sentence import LoadSentences, Sentence


class DeleteBigWords:
    def __init__(self, infile, outfile, deletefile, delete_list):
        self.sentence_loader = LoadSentences(infile)
        self.reader = self.sentence_loader.Reader()
        self.infile = infile
        self.outfile = outfile
        self.deletefile = deletefile
        self.delete_list = delete_list

    def process(self):
        cnt = 0
        with open(self.outfile, 'w') as of:
            with open(self.deletefile, 'w') as df:
                for sentence in tqdm(self.reader):
                    if sentence.cui1 in self.delete_list or sentence.cui2 in self.delete_list:
                        df.writelines(str(sentence))
                        cnt += 1
                    else:
                        of.writelines(str(sentence))
        return cnt
