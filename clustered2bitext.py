#!/usr/bin/env python3

from collections import defaultdict
import os
import sys
import random
random.seed(12345)

def read_clustered(path, langs):
  lang = ['eng'] + langs  # add english to the beginning
  data = []
  with open(path) as fin:
    for line in fin:
      arr = line.strip().split('\t')
      words = defaultdict(list)
      words['eng'].append(arr[0])

      for entry in arr[1:]:
        word, lang = entry.split('/')
        words[lang].append(word)
      data.append([','.join(words[lang]) for lang in langs])
  return data


def get_langs():
  langs = []
  with open('langs') as fin:
    for line in fin:
      langs.append(line.strip())
  return langs


def make_singles(path):
  langs = ['eng'] + get_langs()
  data = read_clustered(path, langs)
  data = list(map(list, zip(*data)))

  for lang, words in zip(langs, data):
    with open('singles/' + lang, 'w') as fout:
      for w in words:
        print(w, file=fout)


def make_bitext(splits=[60,20,20]):
  langs = get_langs()
  with open('pairs', 'w') as fout:
    for tgt in langs:
      assignment = assign_split(tgt)
      for src in langs:
        if src != tgt:
          print(src + ' ' + tgt, file=fout)
          split(src, tgt, splits, assigned=assignment)


def assign_split(lang):
  unk_tgt = []
  has_tgt = []
  if not os.path.exists('singles'):
    os.mkdir('singles')
  with open('singles/' + lang) as fin:
    for index, word in enumerate(fin):
      if word.strip() != '':
        has_tgt.append(index)
      else:
        unk_tgt.append(index)
  random.shuffle(has_tgt)
  return has_tgt, unk_tgt


def tr(word):
  return ' '.join(word)


# 60-20-20 splits by default
def split(src, tgt, splits, assigned=None):
  with open('singles/' + src) as srcfile, open('singles/' + tgt) as tgtfile:
    src_words = srcfile.read().split('\n')
    tgt_words = tgtfile.read().split('\n')

  if assigned is not None:
    known_tgt = [(index, src_words[index], tgt_words[index]) for index in assigned[0]]
    unknown_tgt = [(index, src_words[index], tgt_words[index]) for index in assigned[1]]
  else:
    bitext = list(enumerate(zip(src_words, tgt_words)))
    random.shuffle(bitext)

    known_tgt = [(index, pair[0], pair[1]) for index, pair in bitext if pair[1] != '']
    unknown_tgt = [(index, pair[0], pair[1]) for index, pair in bitext if pair[1] == '']

  split1 = splits[0] * 0.01
  split2 = split1 + splits[1] * 0.01

  train = known_tgt[: int(len(known_tgt) * split1)]
  dev = known_tgt[int(len(known_tgt) * split1) : int(len(known_tgt) * split2)]
  test = known_tgt[int(len(known_tgt) * split2) :]

  train_unk_src = [x for x in train if x[1] == '']  # x = (index, src word, tgt word)
  train_has_src = [x for x in train if x[1] != '']

  dev_unk_src = [x for x in dev if x[1] == '']
  dev_has_src = [x for x in dev if x[1] != '']

  test_unk_src = [x for x in test if x[1] == '']
  test_has_src = [x for x in test if x[1] != '']

  unk_tgt_unk_src = [x for x in unknown_tgt if x[1] == '']
  unk_tgt_has_src = [x for x in unknown_tgt if x[1] != '']

  data_splits = [
      (train_has_src, 'train'),
      (dev_has_src, 'dev'),
      (test_has_src, 'test'),
      (train_unk_src, 'train_unk_src'),
      (dev_unk_src, 'dev_unk_src'),
      (test_unk_src, 'test_unk_src'),
      (unk_tgt_unk_src, 'unk_tgt_unk_src'),
      (unk_tgt_has_src, 'unk_tgt_has_src')]

  for data_split, folder in data_splits:
    if not os.path.exists(folder):
      os.mkdir(folder)

    with open(folder + '/' + src + '-' + tgt + '.idx', 'w') as fout:
      for index, src_word, tgt_word in data_split:
        for sw in src_word.split(','):
          for tw in tgt_word.split(','):
            print(str(index), file=fout)

    with open(folder + '/' + src + '-' + tgt + '.src', 'w') as fout:
      for index, src_word, tgt_word in data_split:
        for sw in src_word.split(','):
          for tw in tgt_word.split(','):
            print(tr(sw), file=fout)

    with open(folder + '/' + src + '-' + tgt + '.tgt', 'w') as fout:
      for index, src_word, tgt_word in data_split:
        for sw in src_word.split(','):
          for tw in tgt_word.split(','):
            print(tr(tw), file=fout)


if __name__ == '__main__':
  make_singles(sys.argv[1])
  make_bitext(splits=[60,20,20])

