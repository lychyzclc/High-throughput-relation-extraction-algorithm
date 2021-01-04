import argparse
import logging
import math
import re
from itertools import islice
from multiprocessing import Process

import spacy

from util.logger import get_logger

logger = logging.getLogger(__name__)


def strip_title(sub_str):
    r = re.search('==+.*?==+', sub_str)
    if r:
        return sub_str[:r.span()[0]]
    else:
        return sub_str


def get_next(string):
    sub_str = ''
    mark = 0
    if re.match('<<<|>>>', string):
        r = re.match('[>>>|<<<].*?==+.*?==+|[>>>|<<<].*?$', string).span()
        sub_str = string[:r[1]]
        sub_str = strip_title(sub_str)
        mark = 0
    elif string.startswith('=='):
        r = re.match('==+.+?==+', string)
        if r:
            sub_str = string[:r.span()[1]]
        else:
            r = re.match('=+', string).span()
            sub_str = string[:r[1]]
        mark = 1
    else:
        r = re.match('.*?==+.*?==+|.*$', string).span()
        sub_str = string[:r[1]]
        sub_str = strip_title(sub_str)
        mark = 2
    split = len(sub_str)
    return sub_str, string[split:], mark


def get_titles(title_list):
    titles = ''
    if len(title_list):
        titles = '.'.join(title_list) + '. ' * (4 - len(title_list))
    else:
        titles = ' . . . '
    return titles


def output(output_file, splitter, lines, n, error_file):
    logger.info('starting subprocess %d...' % n)
    with open(output_file + str(n) + '.txt', 'w', encoding='utf-8') as outfile:
        i = 0
        for line in lines:
            if i % 10 == 0:
                logger.info('subprocess %d: %d finished' % (n, i))
            line_list = line.split('|')
            ID = line_list[0]
            main_title = line_list[1]
            main_title_p = len(ID) + 1
            content = line_list[2].strip()
            content_p = main_title_p + len(main_title) + 1
            title_list = []
            out_list = []
            flag = 1
            sent_num = 0
            if ID.startswith('5') or ID.startswith('6'):
                sents = splitter(main_title)
                for s in sents.sents:
                    s = str(s)
                    temp = main_title_p + main_title.find(s)
                    out_list.append(str(sent_num) + '|' + ID + '|' + '<EMPTY_TITLE>' + '|' +
                                    s.strip() + '|' + ' . . . ' + '|' +
                                    str(temp))
                    sent_num += 1
                while (content):
                    sub, content, mark = get_next(content)
                    if not sub:
                        logger.info('error ' + ID)
                        break
                    if mark == 2:
                        sub = '>>>' + sub
                        content_p -= 3
                    content_list = re.split('>>>|<<<', sub)
                    for con in content_list[1:]:
                        content_p += 3
                        if con.strip().strip('■').strip():
                            try:
                                sents = splitter(con)
                                for s in sents.sents:
                                    s = str(s)
                                    temp = content_p + con.find(s)
                                    out_list.append(str(sent_num) + "|" + ID + '|' +
                                                    '<EMPTY_TITLE>' + '|' +
                                                    s.strip() + '|' +
                                                    ' . . . ' + '|' +
                                                    str(temp))
                                    sent_num += 1
                            except:
                                logger.info('error ' + ID)
                                flag = 0
                        content_p += len(con)
            else:
                while (content):
                    sub, content, mark = get_next(content)
                    if not sub:
                        logger.info('error ' + ID)
                        break
                    if mark == 1:
                        content_p += len(sub)
                        if sub.strip('='):
                            c = sub.count('=') / 2 - 2
                            while (c < len(title_list)):
                                title_list.pop()
                            title_list.append(sub.strip('='))
                    else:
                        if mark == 2:
                            sub = '>>>' + sub
                            content_p -= 3
                        sub_titles = get_titles(title_list)
                        content_list = re.split('>>>|<<<', sub)
                        for con in content_list[1:]:
                            content_p += 3
                            if con.strip().strip('■').strip():
                                try:
                                    sents = splitter(con)
                                    for s in sents.sents:
                                        s = str(s)
                                        temp = content_p + con.find(s)
                                        out_list.append(str(sent_num) + "|" + ID + '|' + main_title +
                                                        '|' + s.strip() + '|' +
                                                        sub_titles + '|' +
                                                        str(temp))
                                        sent_num += 1
                                except:
                                    logger.info('error ' + ID)
                                    flag = 0
                            content_p += len(con)
            if out_list and flag:
                outfile.writelines('\n'.join(out_list) + '\n')
            elif not flag:
                with open(error_file, 'a+') as f:
                    f.writelines(line)
            i += 1
        logger.info('subprocess %d: all finished' % (n))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file',
                        type=str,
                        help='The path to input file')
    parser.add_argument('--text_length',
                        type=str,
                        help='The num of rows of the input file')
    parser.add_argument('--output_file',
                        type=str,
                        help='The path to output file')
    parser.add_argument('--error_file',
                        type=str,
                        help='The path to output error')
    parser.add_argument('--log_file',
                        type=str,
                        help='The path to output log')
    parser.add_argument('--proc',
                        default=None,
                        help='process number for multiprocess')

    args = parser.parse_args()

    logger = get_logger(logger, args.log_file)

    splitter = spacy.load('en_core_web_sm')

    if args.proc is not None:
        text_list = []
        n = int(math.ceil(int(args.text_length) / int(args.proc)))
        with open(args.input_file) as infile:
            p_list = []
            for i in range(8):
                next_n_lines = list(islice(infile, n))
                p = Process(target=output,
                            args=(args.output_file, splitter, next_n_lines, i,
                                  args.error_file))
                p.start()
                p_list.append(p)
            for ap in p_list:
                ap.join()
    else:
        with open(args.input_file) as infile:
            lines = infile.readlines()
            output(args.output_file, splitter, lines, 0, args.error_file)
