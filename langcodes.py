#!/usr/bin/env python3

import os.path
import re
import sys
import urllib.request
from itertools import groupby
from collections import defaultdict


def get_langs_from_file(filename):
  if os.path.isfile(filename):
    with open(filename) as fin:
      return [line.strip() for line in fin.readlines() if line.strip() != '']


def get_langs(family):
  langs = get_langs_from_ethnologue(family)
  langs = [macrolang(x) for x in langs]
  langs = remove_dups(langs)
  return langs


def get_langs_from_ethnologue(family):
  url = 'https://www.ethnologue.com/subgroups/' + family + '-0'
  headers = {'User-Agent': 'Mozilla/5.0'}  # ethnologue refuses request without this
  req = urllib.request.Request(url, headers=headers)
  f = urllib.request.urlopen(req)
  html = f.read().decode()

  langs = []
  for match in re.finditer('\[(...)\]', html):
    lang = match.group(1)
    if lang.isalpha():
      langs.append(lang)

  return langs


def parse_macrolangs(filename):
  with open(filename) as fin:
    macrolangs = {}
    current = ''

    for line in fin:
      arr = [x.strip() for x in line.split('\t')]
      if len(arr[0]) != 0:
        current = arr[0]
        macrolangs[arr[2]] = current
      else:
        macrolangs[arr[1]] = current

    return macrolangs


def macro2microlangs(macrolangs):
  microlangs = defaultdict(list)
  for macro, micro_group in groupby(sorted(macrolangs.items(), key=lambda x: (x[1], x[0])), lambda x: x[1]):
    for micro in micro_group:
      microlangs[macro].append(micro[0])
  return microlangs

macrolangs = parse_macrolangs('/home/wwu/wordalign/data/macrolangs.csv')
microlangs = macro2microlangs(macrolangs)


def macrolang(lang):
  return macrolangs.get(lang, lang)


def remove_dups(seq):
  '''
  preserves order, see
  http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
  '''
  seen = set()
  seen_add = seen.add
  return [x for x in seq if not (x in seen or seen_add(x))]


if __name__ == '__main__':
  for lang in get_langs(sys.argv[1]):
    print(lang)
