from tqdm import tqdm

from load_general_clean_sentence import LoadSentences, Sentence


class RemoveUp:
    def __init__(self, infile, outfile, deletefile):
        self.sentence_loader = LoadSentences(infile)
        self.infile = infile
        self.outfile = outfile
        self.deletefile = deletefile

    def init(self, nearpardic_file, nearrbdic_file, neardic_file):
        print('- loading updic...')
        file = open(nearpardic_file, 'r')
        self.nearpardic = eval(file.read())
        file.close()
        file = open(nearrbdic_file, 'r')
        self.nearrbdic = eval(file.read())
        file.close()
        file = open(neardic_file, 'r')
        self.neardic = eval(file.read())
        file.close()
        self.dic = {}
        print('- done')
        print('- loading sentences...')
        self.reader = self.sentence_loader.Reader()
        print('- done')

    def findup(self,cui):
        if cui in self.dic.keys():
            return self.dic[cui]
        else:
            a1 = self.nearpardic.get(cui, [])
            a2 = self.nearrbdic.get(cui, [])
            a3 = self.neardic.get(cui, [])
            a = a1 + a2 + a3
            b1 = sum([self.nearpardic.get(i, []) for i in a], [])
            b2 = sum([self.nearrbdic.get(i, []) for i in a], [])
            b3 = sum([self.neardic.get(i, []) for i in a], [])
            b = b1 + b2 + b3
            c1 = sum([self.nearpardic.get(i, []) for i in b], [])
            c2 = sum([self.nearrbdic.get(i, []) for i in b], [])
            c3 = sum([self.neardic.get(i, []) for i in b], [])
            c = c1 + c2 + c3
            final = a + b + c
            self.dic[cui] = final
            return final

    def process(self):
        cnt = 0
        with open(self.outfile, 'w') as of:
            with open(self.deletefile, 'w') as df:
                for sentence in tqdm(self.reader):
                    cui1 = sentence.cui1
                    cui2 = sentence.cui2
                    cui1_up = self.findup(cui1)
                    if cui2 in cui1_up:
                        cnt += 1
                        df.writelines(str(sentence))
                    else:
                        cui2_up = self.findup(cui2)
                        if cui1 in cui2_up:
                            cnt += 1
                            df.writelines(str(sentence))
                        else:
                            of.writelines(str(sentence))
        return cnt

if __name__ == '__main__':
    remover = RemoveUp(input_file, output_file, delete_file)
    remover.init(nearpardic_file, nearrbdic_file, neardic_file)
    remover.process()
