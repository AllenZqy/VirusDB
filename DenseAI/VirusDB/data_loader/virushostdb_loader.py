# -*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import os
import logging
import json

word_dict = {}
label_dict = {}
ner_dict = {}


def _parse_db_text(file_name: str, word_index_from=5, label_index_from=3, lower=True, sent_delimiter='\t'):
    """
    Parse virushostdb.tsv
    """
    virus_entities = []
    refseq_set = set()
    if os.path.exists(file_name) is False:
        logging.error("File is not exists: {}".format(file_name))
        return virus_entities, refseq_set

    try:
        file = open(file_name, 'r', encoding="utf-8")
        index = 0
        for line in file:

            if index == 0:
                index += 1
                continue

            # Replace '\n'
            if len(line) > 0:
                line = line[:-1]

            # virus tax id,
            # virus name,
            # virus lineage,
            # refseq id,
            # KEGG GENOME,
            # KEGG DISEASE,
            # DISEASE
            # host tax id
            # host name
            # host lineage
            # pmid
            # evidence
            # sample type
            # source organism
            # 存在 一个 virus tax id 对多个 refseq id 和 对个 host tax id的场景
            tokens = line.split(sent_delimiter)
            if len(tokens) < 14:
                continue

            virus_tax_id = tokens[0]

            refseq_ids = tokens[3]
            refseq_tokens = refseq_ids.split(',')
            if refseq_tokens is None or len(refseq_tokens) == 0:
                continue

            host_tax_id = tokens[7]

            for refseq in refseq_tokens:
                refseq = refseq.strip()
                refseq = refseq.lower()
                virus_entity = {}
                virus_entity['virus_tax_id'] = virus_tax_id
                virus_entity['virus name'] = tokens[1]
                virus_entity['virus lineage'] = tokens[2]
                virus_entity['refseq_id'] = refseq
                virus_entity['host_tax_id'] = host_tax_id
                virus_entity['host name'] = tokens[8]
                virus_entity['host lineage'] = tokens[9]
                virus_entity['DISEASE'] = tokens[6]
                virus_entities.append(virus_entity)

                refseq_set.add(refseq.lower())
                #print(virus_entity)
                #print()
            index += 1
    except Exception as e:
        logging.error(e)

    return virus_entities, refseq_set



def _parse_genomic_text(file_name: str, refseq_set:set=None, word_index_from:int=5, label_index_from:int=3, lower:bool=True, sent_delimiter:str='\t'):
    """
    Parse virushostdb.tsv
    """
    refseq_entities = {}
    if os.path.exists(file_name) is False:
        logging.error("File is not exists: {}".format(file_name))
        return refseq_entities

    try:
        file = open(file_name, 'r', encoding="utf-8")
        index = 0

        refseq_id = ''
        refseq = ''
        for line in file:
            # Replace '\n'
            if len(line) > 0:
                line = line[:-1]

            if line.startswith('>'):
                # Replace '>' and '||'
                line = line[1:-2]

                if len(refseq_id) > 0 and len(refseq) > 0:
                    refseq_id = refseq_id.lower()

                    # Check refseq_id
                    if refseq_set is not None and refseq_id in refseq_set:
                        refseq_entities[refseq_id] = refseq
                        if len(refseq_entities) == 10:
                            print(refseq)
                    else:
                        print(refseq_id)

                refseq_id = ''
                refseq = ''
                # Sequence_accession virus name
                # Hostname
                # Virus lineage
                # Host lineage
                # Sample type
                # Taxonomic identifier
                tokens = line.split('|')
                if len(tokens) < 1:
                    continue

                # refseq_id
                for ii in range(len(tokens[0])):
                    if tokens[0][ii] == ' ':
                        break
                    refseq_id += tokens[0][ii]

                #print(refseq_id)
            else:
                refseq += line
            index += 1

        if len(refseq_id) > 0 and len(refseq) > 0:
            refseq_id = refseq_id.lower()
            # Check refseq_id
            if refseq_set is not None and refseq_id in refseq_set:
                refseq_entities[refseq_id] = refseq

    except Exception as e:
        logging.error(e)

    print(index)
    return refseq_entities


def _parse_text(file_name: str, word_index_from=5, label_index_from=3, lower=True, sent_delimiter='\t'):
    """
    Read corpus 读取语料
    :param file_name:文件名称
    :param word_index_from: 词语开始编号
    :param label_index_from: 标签开始编号
    :param lower: 转化为小写
    :param sent_delimiter: 词语分隔符
    :param padding: 是否填充
    :return:
    """
    file = open(file_name, 'r', encoding="utf-8")
    words = []
    labels = []
    ner_labels = []
    # for line in file:
    #     line = line[:-1]
    #     word = []
    #     label = []
    #     ner = []
    #
    #     CLS = '[CLS]'
    #
    #     if len(line) > 0:
    #         tags, chars = line.split(sent_delimiter)
    #         if lower:
    #             chars = str(chars).lower()
    #             tags = str(tags).lower()
    #
    #         # Words
    #         if CLS not in word_dict.keys():
    #             word_dict[CLS] = len(word_dict) + word_index_from
    #         word.append(word_dict[CLS])
    #         for ii in range(len(chars)):
    #             char = chars[ii]
    #             if char not in word_dict.keys():
    #                 word_dict[char] = len(word_dict) + word_index_from
    #             word.append(word_dict[char])
    #
    #         ner_tags = np.zeros(len(chars) + 1, dtype=np.int)
    #         if ac_dic is not None:
    #             ac_words, ac_texts = map_cut(chars, ac_dic)
    #             # print(ac_words)
    #             for ac_word in ac_words[0]:
    #                 # print("Ac_word: ", ac_word)
    #                 tag = get_named_entity([ac_word[0]], disease_dict=disease_dict, body_dict=body_dict,
    #                                        symptom_dict=symptom_dict, check_dict=check_dict)
    #                 # print(tag)
    #                 start = ac_word[1]
    #                 word_len = ac_word[2]
    #                 if len(tag) > 0 and word_len > 0:
    #                     for jj in range(word_len):
    #                         if ner_tags[start + 1 + jj] == 0:
    #                             tag = tag[0]
    #                             if tag not in ner_dict.keys():
    #                                 ner_dict[tag] = len(ner_dict) + 1
    #                             ner_tags[start + 1 + jj] = ner_dict[tag]
    #                     # if tag[0] not in word_dict.keys():
    #                     #    word_dict[tag[0]] = len(word_dict) + word_index_from
    #                     # word.append(word_dict[tag[0]])
    #
    #                 # 把分词也放进来
    #                 char = ac_word[0]
    #                 if char not in word_dict.keys():
    #                     word_dict[char] = len(word_dict) + word_index_from
    #                 word.append(word_dict[char])
    #
    #             # 2-grams
    #             for ii in range(len(ac_words[0])):
    #                 if ii + 1 < len(ac_words[0]):
    #                     char = ac_words[0][ii][0] + ac_words[0][ii + 1][0]
    #                     #print("char:", char)
    #                     if char not in word_dict.keys():
    #                        word_dict[char] = len(word_dict) + word_index_from
    #                     word.append(word_dict[char])
    #
    #         # print("NER: ", ner_tags)
    #
    #         # Tags
    #         if tags not in label_dict.keys():
    #             label_dict[tags] = len(label_dict) + label_index_from
    #         label.append(label_dict[tags])
    #
    #         if len(word) > 0 and len(label) > 0:
    #             words.append(np.array(word))
    #             labels.extend(np.array(label))
    #             ner_labels.append(ner_tags)

    # print("words: ", words)
    # print("labels: ", labels)
    # print("ner_labels: ", len(ner_labels), ner_labels)
    return words, labels, ner_labels


def load_data(train_paths: list,
              valid_paths: list,
              test_paths: list,
              num_words=None,
              max_seq_len=25,
              word_index_from=5,
              label_index_from=3,
              lower=True,
              sent_delimiter='\t',
              padding=False,
              word_dict: dict = None,
              label_dict: dict = None,
              add_to_dict=True,
              **kwargs):
    """
    Load dataset 读取数据集
    """

    if word_dict is None:
        word_dict = {}
        word_dict["[SEP]"] = 1
        word_dict["[CLS]"] = 2
        word_dict["[MASK]"] = 3
        word_dict["[UNK]"] = 4

    if label_dict is None:
        label_dict = {}
        label_dict["[CLS]"] = 1
        label_dict["[UNK]"] = 2

    # Load Train set 读取训练语料
    x_train = []
    y_train = []
    count = 0
    if train_paths != None and len(train_paths):
        for file_name in train_paths:
            words, labels = _parse_text(file_name, word_index_from=word_index_from, label_dict=label_dict, sent_delimiter=sent_delimiter)

            x_train.extend(words)
            labels_train.extend(labels)
            ner_labels_train.extend(ner_labels)

    x_train = np.array(x_train)
    labels_train = np.array(labels_train)
    ner_labels_train = np.array(ner_labels_train)

    print("x_train: ", x_train.shape)
    print("labels_train: ", labels_train.shape)
    print("ner_labels_train: ", ner_labels_train.shape)

    x_test = []
    labels_test = []
    ner_labels_test = []
    count = 0
    if test_paths != None and len(test_paths) >= 0:
        for file_name in test_paths:
            words, labels, ner_labels = _parse_text(file_name, ac_dic=ac_dic, disease_dict=disease_dict,
                                                    body_dict=body_dict, symptom_dict=symptom_dict,
                                                    check_dict=check_dict)
            x_test.extend(words)
            labels_test.extend(labels)
            ner_labels_test.extend(ner_labels)

    print("Test Counter: ", count)

    x_test = np.array(x_test)
    labels_test = np.array(labels_test)
    ner_labels_test = np.array(ner_labels_test)

    print("x_test: ", x_test.shape)
    print("labels_test: ", labels_test.shape)
    print("ner_labels_test: ", ner_labels_test.shape)

    src_tokenizer = Tokenizer(filters='\t\n', oov_token="[UNK]")
    tgt_tokenizer = Tokenizer(filters='\t\n', oov_token="[UNK]")

    print("word_dict: ", len(word_dict))
    print("label_dict: ", len(label_dict))
    print("ner_dict: ", len(ner_dict))

    src_tokenizer.word_index = dict((w, c) for w, c in word_dict.items())
    src_tokenizer.index_word = dict((c, w) for w, c in word_dict.items())

    tgt_tokenizer.word_index = dict((w, c) for w, c in label_dict.items())
    tgt_tokenizer.index_word = dict((c, w) for w, c in label_dict.items())

    src_tokenizer.num_words = len(src_tokenizer.word_index) + word_index_from - 4
    tgt_tokenizer.num_words = len(tgt_tokenizer.word_index) + label_index_from - 2

    if maxlen and padding:
        x_train, ner_labels_train = _remove_long_seq(maxlen, x_train, ner_labels_train)
        if not x_train:
            raise ValueError('After filtering for sequences shorter than maxlen=' +
                             str(maxlen) + ', no sequence was kept. '
                                           'Increase maxlen.')
        x_train, ner_labels_train = _pad_sequences(maxlen, x_train, ner_labels_train)
        x_train = np.array(x_train)
        labels_train = np.array(labels_train)
        ner_labels_train = np.array(ner_labels_train)

        x_test, ner_labels_test = _remove_long_seq(maxlen, x_test, ner_labels_test)
        if not x_test:
            raise ValueError('After filtering for sequences shorter than maxlen=' +
                             str(maxlen) + ', no sequence was kept. '
                                           'Increase maxlen.')
        x_test, ner_labels_test = _pad_sequences(maxlen, x_test, ner_labels_test)
        x_test = np.array(x_test)
        labels_test = np.array(labels_test)
        ner_labels_test = np.array(ner_labels_test)

    if not num_words:
        num_words = src_tokenizer.num_words
        num_labels = tgt_tokenizer.num_words

    print("x_train: ", x_train.shape)
    print("labels_train: ", labels_train.shape)
    print("ner_labels_train: ", ner_labels_train.shape)
    print("x_test: ", x_test.shape)
    print("labels_test: ", labels_test.shape)
    print("ner_labels_test: ", ner_labels_test.shape)

    return (x_train, labels_train, ner_labels_train), (x_test, labels_test,
                                                       ner_labels_test), num_words, num_labels, src_tokenizer, tgt_tokenizer, word_dict, label_dict, ner_dict


def _remove_long_seq(maxlen, seq, ner_label=None):
    """Removes sequences that exceed the maximum length.

    # Arguments
        maxlen: Int, maximum length of the output sequences.
        seq: List of lists, where each sublist is a sequence.
        label: List where each element is an integer.

    # Returns
        new_seq, new_label: shortened lists for `seq` and `label`.
    """
    new_seq, new_label, new_ner = [], [], []
    count = 0
    for x, y in zip(seq, ner_label):
        if len(x) < maxlen:
            new_seq.append(x)
            new_ner.append(y)
        else:
            new_seq.append(x[0:maxlen])
            new_ner.append(y[0:maxlen])
            count += 1
    print("Remove: ", count)
    return new_seq, new_ner  # , new_value


def _pad_sequences(maxlen, seq, ner_label=None, pad_x=0, pad_y=0, pad_v=0):
    """Removes sequences that exceed the maximum length.

    # Arguments
        maxlen: Int, maximum length of the output sequences.
        seq: List of lists, where each sublist is a sequence.
        label: List where each element is an integer.

    # Returns
        new_seq, new_label: shortened lists for `seq` and `label`.
    """
    new_seq, new_label, new_ner = [], [], []
    for x, y in zip(seq, ner_label):
        x = list(x)
        y = list(y)
        if len(x) < maxlen:
            pads_x = x + [pad_x] * (maxlen - len(x))
            pads_y = y + [pad_y] * (maxlen - len(y))
            new_seq.append(pads_x)
            new_ner.append(pads_y)
        else:
            new_seq.append(x[0:maxlen])
            new_ner.append(y[0:maxlen])

    return new_seq, new_ner



if __name__ == '__main__':
    train_paths = [
        "F:\\Research\\Data\\medical\\train.txt",
        # "E:\\Research\Corpus\\pku_training_bies",
        # "E:\\Research\Corpus\\weibo_train_bies",
        # "E:\\Research\Corpus\\people_2014_train_bies",
        # "E:\\Research\Corpus\\people_1998_train_bies",
    ]

    virushostdb_file = 'D:\\迅雷下载\\VirusHostDb\\virushostdb.tsv'
    virus_entities, refseq_set = _parse_db_text(virushostdb_file)

    virus_genomic_file = 'D:\\迅雷下载\\VirusHostDb\\virushostdb.formatted.genomic.fna'
    refset_entities = _parse_genomic_text(virus_genomic_file, refseq_set=refseq_set)

    print(len(refset_entities))

    seq_lens = []

    output_file = 'E:\\Research\\Medical\\Data\\virus_host_db.txt'
    with open(output_file, "w") as fh:
        for virus_entity in virus_entities:
            refseq_id = virus_entity['refseq_id']
            refseq_id = refseq_id.lower()
            if refseq_id not in refset_entities.keys():
                print(virus_entity)

            virus_entity['refseq'] = refset_entities[refseq_id]

            seq_len = len(refset_entities[refseq_id])
            seq_lens.append(seq_len)
            if seq_len > 40 * 1024:
                print(seq_len)
            fh.write(json.dumps(virus_entity) + '\n')



    seq_lens = np.array(seq_lens)
    print("Max len: ", max(seq_lens))
    print("Min len: ", min(seq_lens))
    print("Mean len: ", np.mean(seq_lens))

