#!/usr/bin/env python3

from collections import namedtuple
import csv
import functools
from itertools import groupby
import os
import os.path
import pycountry
import sys

import config
import langcodes

@functools.lru_cache(maxsize=None)
def to3(lang_code):
  try:
    return pycountry.languages.get(iso639_1_code=lang_code).iso639_3_code
  except:
    return None


Word = namedtuple('Word', ['foreign', 'english', 'lang', 'pos', 'meaning_id'])

def extend_with_microlangs(langs):
  all_langs = list(langs)
  for lang in langs:
    for micro in langcodes.microlangs[lang]:
      all_langs.append(micro)
  return all_langs


def gather_from_wiktionary(langs):
  langs = set(extend_with_microlangs(langs))  # use set to speed up lookup

  with open(config.wiktionary_location) as fin:
    entries = []
    reader = csv.reader(fin, delimiter='\t', quoting=csv.QUOTE_NONE)
    next(reader, None)  # skip header
    for arr in reader:
      # e, f, en, lang, pos, gender
      if arr[2] == 'en' and to3(arr[3]) in langs:
        entries.append(Word(arr[1].strip(), arr[0].strip(), langcodes.macrolang(to3(arr[3])), arr[4].strip(), None))

      # f, e, lang, en, pos, gender
      elif arr[3] == 'en' and to3(arr[2]) in langs:
        entries.append(Word(arr[0].strip(), arr[1].strip(), langcodes.macrolang(to3(arr[2])), arr[4].strip(), None))

    return entries


def gather_from_panlex(langs):
  langs = extend_with_microlangs(langs)

  entries = []
  for lang in langs:
    filename = config.panlex_location.format(lang)
    if not os.path.isfile(filename):
      continue

    with open(filename) as fin:
      reader = csv.reader(fin)
      next(reader, None)  # skip header
      for f, e, meaning_id, pos in reader:
        entries.append(Word(f.strip(), e.strip(), langcodes.macrolang(lang), None, meaning_id.strip()))  # ignore pos

  return entries


def gather(langs, extra_dicts, output_file):
  wik_words = gather_from_wiktionary(langs)
  print('wiktionary:', len(wik_words))

#  pan_words = gather_from_panlex(langs)
#  print('panlex:', len(pan_words))

  # gather words from extra dictionaries, must be in f \t e \t lang \t pos format
#  extras = []
#  for filename in extra_dicts:
#    with open(filename) as fin:
#      reader = csv.reader(fin, delimiter='\t', quoting=csv.QUOTE_NONE)
#      for f, e, lang, pos in reader:
#        extras.append(Word(f.strip(), e.strip(), langcodes.macrolang(lang), pos.strip(), None))
#  print('extras:', len(extras))

  # merge results
  combined = wik_words #+ pan_words + extras
  combined = sorted(combined, key=lambda x: (x.english, x.foreign, x.lang))  # groupby needs this to be sorted

  #os.makedirs(os.path.dirname(output_file), exist_ok=True)
  with open(output_file, 'w') as fout:
    for key, group in groupby(combined, lambda x: (x.english, x.foreign, x.lang)):
      pos = list(set([normalize_pos(x.pos) for x in group if x.pos is not None and x.pos is not '']))
      meaning_id = list(set([x.meaning_id for x in group if x.meaning_id is not None]))
      #fout.write('\t'.join([key[1], key[0], key[2], '/'.join(pos), '/'.join(meaning_id)]) + '\n')

      foreign, english, lang = key
      fout.write('\t'.join([  # backtrans, POS, meaning ids
        english, foreign, lang, '', '/'.join(pos), '']) + '\n')



def normalize_pos(pos):
  pos = pos.upper()
  if pos == 'ADJECTIVE':
    pos = 'ADJ'
  return pos


def read_file(filename):
  with open(filename) as fin:
    result = []
    for line in fin:
      result.append(line.strip())
    return result


if __name__ == '__main__':
  if len(sys.argv) == 3:
    langs = read_file(sys.argv[1])
    gather(langs, [], sys.argv[2])  # skip extra dictionaries for now
  else:
    print('Usage: gather.py LANGS_FILE OUTPUT_FILE')
