import re
import string


class TitleAsSent:
    def __init__(self):
        self.sents = []

    def insert(self, text):
        if text in self.sents:
            return False
        else:
            self.sents.append(text)
            return True

class Sentence:
    def __init__(self, line_list):
        self.article_id = line_list[0]
        self.sent_id = line_list[1]
        self.title = line_list[2].lower()
        if not self.title:
            self.title = '<empty_title>'
        self.text = line_list[3].lower()
        self.article_structure = line_list[4].lower()
        self.start1 = int(line_list[5])
        self.end1 = int(line_list[6])
        self.entity1 = line_list[7]
        self.cui1 = line_list[8]
        self.type1 = line_list[9]
        self.is_title1 = int(line_list[10])
        self.start2 = int(line_list[11])
        self.end2 = int(line_list[12])
        self.entity2 = line_list[13]
        self.cui2 = line_list[14]
        self.type2 = line_list[15]
        self.is_title2 = int(line_list[16])
        self.text_length = len(self.text.split())
        self.pos1 = []
        self.pos2 = []
        self.is_proper_sentence = self.text_length > 5
        self.entity_in_sent = not (self.is_title1 and self.is_title2)
        self.has_empty_title = self.title == '<empty_title>'

    def mask(self, mask_list):
        self.mask1 = mask_list[0]
        self.mask2 = mask_list[1]
        mark1 = ' ' + self.mask1 + ' '
        mark2 = ' ' + self.mask2 + ' '
        text = self.text
        title = self.title
        if not self.is_title1 and not self.is_title2:
            pos_list = [self.start1, self.end1, self.start2, self.end2]
            pos_list.sort()
            if self.start2 > self.end1:
                    self.text = text[:pos_list[0]] + mark1 + text[pos_list[1]:pos_list[2]] + mark2 + \
                            text[pos_list[3]:]
            else:
                self.text = text[:pos_list[0]] + mark2 + text[pos_list[1]:pos_list[2]] + mark1 + \
                            text[pos_list[3]:]
        elif self.is_title1:
            self.title = title[:self.start1] + mark1 + title[self.end1:]
            self.text = text[:self.start2] + mark2 + text[self.end2:]
        elif self.is_title2:
            self.title = title[:self.start2] + mark2 + title[self.end2:]
            self.text = text[:self.start1] + mark1 + text[self.end1:]
        self.text = re.sub(r'[ ]+', ' ', self.text).strip()
        self.title = re.sub(r'[ ]+', ' ', self.title).strip()


    def handle_punc(self, text):
        punc = string.punctuation.replace('%', '').replace('_', '').replace('-', '').replace('+', '').replace('/', '').replace('.', '')
        punc += '±'
        result = re.findall('[a-z ]/[a-z ]|.\. ', text)
        for r in result:
            text = text.replace(r, r[0]+' '+r[1]+' '+r[2])
        result = re.findall('.\.$', text)
        for r in result:
            text = text.replace(r, r[0]+' '+r[1])
        for p in punc:
            text = text.replace(p, ' ' + p + ' ')
        text = re.sub(r'[ ]+', ' ', text).strip()
        return text

    def calculate_pos(self):
        if not self.has_empty_title:
            self.title = self.handle_punc(self.title)
        self.text = self.handle_punc(self.text)
        self.text_length = len(self.text.split())
        text_all = self.title + ' . ' + self.text
        word_list = text_all.split()
        index1 = None
        index2 = None
        if self.mask1 != self.mask2:
            index1 = word_list.index(self.mask1)
            index2 = word_list.index(self.mask2)
        else:
            if not self.is_title1 and not self.is_title2:
                if self.end1 < self.start2:
                    index1 = word_list.index(self.mask1)
                    index2 = word_list[index1+1:].index(self.mask2)+index1+1
                else:
                    index2 = word_list.index(self.mask2)
                    index1 = word_list[index2+1:].index(self.mask1)+index2+1
            elif self.is_title1:
                index1 = word_list.index(self.mask1)
                index2 = word_list[index1+1:].index(self.mask2)+index1+1
            else:
                assert self.is_title2
                index2 = word_list.index(self.mask2)
                index1 = word_list[index2+1:].index(self.mask1)+index2+1
        for i, word in enumerate(word_list):
            self.pos1.append(abs(i-index1))
            self.pos2.append(abs(i-index2))

    def __str__(self):
        return str(self.article_id)+'|'+str(self.sent_id)+'|'+str(self.cui1) + '|'+ str(self.type1) + '|' + str(self.cui2) +\
                '|' + str(self.type2)+'|'+str(self.title)+' <sep> '+str(self.text)+'|'+ \
                str(self.article_structure)+'|'+str(self.pos1)+'|'+str(self.pos2)+ '|'+ str(self.text_length)\
                +'|'+str(self.is_title1)+'|'+str(self.is_title2) + '\n'


class LoadSentences:
    def __init__(self, filepath):
        self.filepath = filepath

    def Process(self, line):
        line = line.replace(u'\xa0', u' ').replace(u'\u200a', u' ').replace(u'\u2009', u' ')
        line_list = line.strip().split('|')
        return Sentence(line_list)

    def Reader(self):
        f = open(self.filepath, encoding='utf-8')
        line = f.readline()
        while line:
            yield self.Process(line)
            line = f.readline()
        f.close()
