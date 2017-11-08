#-*-coding:utf8-*-
import os
import re
import sys
sys.path.append("../")
import time
import json
import codecs
import argparse
import jieba
from datetime import datetime

reload(sys)
sys.setdefaultencoding( "utf-8" )


parser = argparse.ArgumentParser()
parser.add_argument('--stop_word', help = "stop words list")
parser.add_argument('--complex_simple', help = "complex to simple list")
parser.add_argument('--userdict', help = "user dict")
args = parser.parse_args()

jieba.load_userdict(args.userdict)

def complex_to_simple():
    com2sim = {}
    com = []
    sim = []
    # The input file has two columns: cmmplex and simple
    with open(args.complex_simple, 'r') as dict_file:
        for line in dict_file:
            item = line.strip().split('\t')
            if len(item) != 2:
                pass
            else:
                com.append(item[0].strip())
                sim.append(item[1].strip())
    com2sim = dict(zip(com, sim))
    return com2sim


def get_stopwords():                          
    stop_w = []                               
                                              
    # The input file has only one column.     
    stop_word_file = open(args.stop_word, 'r')
                                              
    for line in stop_word_file:               
        line = line.strip()                   
        stop_w.append(line)                   
                                              
    stop_word_file.close()                    
                                              
    return  stop_w                            

def is_chinese(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    if u'\u0030' <= uchar <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
        return True
    else:
        return False 


def is_norm(uchar):
    if (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False
    return True

def transform_code(item):
    gbk_item = ''
    utf8_item = ''

    try:
        utf8_item = item.decode('utf8')
    except:
        return None

    flag = 0

    try:
        gbk_item = utf8_item.encode('gbk')
    except:
        flag = 1

    if flag == 1:

        itemarr = []

        for uc in utf8_item:
            
            try:
                gc = uc.encode('gbk')
                itemarr.append(gc)
            except:
                itemarr.append(' ')

        gbk_item=''.join(itemarr)

    return gbk_item


def check_valid(gbk_item):
    i = 0 
    valid = True                                                                        
    while i < len(gbk_item):
        ascc = ord(gbk_item[i])
        if ascc < 128:
            i += 1
            continue
        else:
            if i + 1 >= len(gbk_item):
                valid = False
                break
            else:
                ascc_next = ord(gbk_item[i + 1])
                if ascc < 0x81 or ascc > 0xfe:
                    valid = False
                    break
                else:
                    if (ascc_next >= 0x40 and ascc_next <= 0x7e) or (ascc_next >= 0x80 and ascc_next <= 0xfe):
                        pass
                    else:
                        valid = False
                        break
            i += 2
    return valid


def string_filter(item):
    item = item.strip()
    gbk_item = transform_code(item)

    if gbk_item is None  or (not check_valid(gbk_item)):
        return ''

    else:
        return item


def complex_to_simple():
    com2sim = {}

    com = []
    sim = []

    # The input file has two columns: cmmplex and simple
    with open(args.complex_simple, 'r') as dict_file:

        for line in dict_file:

            item = line.strip().split('\t')

            if len(item) != 2:
                pass

            else:
                com.append(item[0].strip())
                sim.append(item[1].strip())

    com2sim = dict(zip(com, sim))

    return com2sim


def query_bc_to_dbc(query):
    rstring = ""

    for uchar in query:

        inside_code=ord(uchar)

        if inside_code == 12288:                              
            inside_code = 32

        elif (inside_code >= 65281 and inside_code <= 65374): 
            inside_code -= 65248

        rstring += unichr(inside_code)

    return rstring



def query_filter(word):
    # Get the mapping of cmplex and simple.
    simple_dict = complex_to_simple()

    # Get the stop words list.
    stop_w = get_stopwords()

    # Check the validity of the word.
    query = string_filter(word)

    if query == '':
        return ''
    iline = query.strip().decode('utf8')

    iline = iline.strip()
    if not iline.isdigit():

        oline = query_bc_to_dbc(iline)

        # convert the complex to simple.
        for uchar in oline:
            if uchar != '.' and uchar != '-' and uchar != '~' and uchar != '～':
                if not is_norm(uchar):
                    oline = oline.replace(uchar, ' ')
                if uchar in simple_dict:
                    oline = oline.replace(uchar, simple_dict[uchar])
        oline = oline.strip()

        return oline
    else:
        return ''

def sequence_cut(query):
    result = ""
   
    query_list = query.split()
    for it in query_list:
        if len(it) >= 6:
            query_cut = jieba.cut(it, cut_all=False)
            result += ' '.join(query_cut)
            # rst = ('\t'.join(query_cut)).split('\t')
            # result.extend(query_cut)
        else:
            result += ' ' + it
    # title = '\t'.join(result)
    return result
    # return title



# Start to process the input data. The input data has only one column, query.
for line in sys.stdin:
    fields = line.rstrip('\n').split("\t")
    if len(fields) != 3:
        continue

    [sku_id, title, query] = fields

    title_cut = sequence_cut(title.replace('"',''))
    query_cut = sequence_cut(query.replace('"',''))

    query_words = re.findall('\((.*?)\)', query_cut)

    print "{}\t{}\t{}".format(sku_id, title_cut, " ".join(query_words))
