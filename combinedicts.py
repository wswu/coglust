#!/usr/bin/env python3

import sys

if __name__ == '__main__':
  data = []
  for filename in sys.argv[1:]:
    with open(filename) as fin:
      lang = filename[-3:]
      for line in fin:
        e, f, backtrans, tr_score, meaning_ids = line.strip('\n').split('\t')
        data.append([f, e, lang, backtrans, '', meaning_ids])

  data.sort(key=lambda x: (x[1], x[0]))  # key=(x.english, x.foreign)
  for row in data:
    print('\t'.join(row))
