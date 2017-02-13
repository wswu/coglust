#!/usr/bin/env python3

import sys
from collections import defaultdict

BLANK = '---'

def format(number):
  if number == BLANK:
    return number
  else:
    return '{:.2f}'.format(number).replace('0.', '.')  # remove leading zero


with open(sys.argv[1]) as fin:
  fin.readline()  # skip header
  numbers1 = defaultdict(lambda: BLANK)
  numbers10 = defaultdict(lambda: BLANK)
  mrr = defaultdict(lambda: BLANK)
  langs = set()

  for line in fin:
    arr = line.strip().split(',')
    src, tgt = arr[0][arr[0].rfind('/') + 1 :].split('-')
    langs.add(src)
    langs.add(tgt)

    numbers1[(src, tgt)] = float(arr[1])
    numbers10[(src, tgt)] = float(arr[2])
    mrr[(src, tgt)] = float(arr[3])

  langs = sorted(langs)

  for data in [numbers1, numbers10, mrr]:
    print(r'\begin{tabular}{' + 'l' * (len(langs) + 1) + '}')
    print(r'  \toprule')
    print(r'  {\tiny\backslashbox{src}{tgt}} & ')
    print('        ' + ' & '.join(langs) + r' \\')
    print(r'  \midrule')
    for src in langs:
      print('  ' + src + ' & ' + ' & '.join([format(data[(src, tgt)]) for tgt in langs]) + r' \\')
    print(r'  \bottomrule')
    print(r'\end{tabular}')
    print()



