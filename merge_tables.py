#!/usr/bin/env python3

from collections import Counter
from itertools import groupby
import sys

'''
Merge tables from Panlex and Wiktionary.

Table format is for \t eng \t lang \t backtrans \t pos \t meaningID/meaningId/etc.
'''

def main():
  data = []
  for table in sys.argv[1:]:
    with open(table) as fin:
      for line in fin:
        arr = line.strip('\n').split('\t')
        data.append(arr)

  combined = []

  data.sort(key=lambda x: (x[0], x[1], x[2]))
  for key, group in groupby(data, key=lambda x: (x[0], x[1], x[2])):
    backtrans = []
    poses = set([])
    meaning_ids = set([])

    for row in group:
      foreign, eng, lang, bt, pos, ids = row
      backtrans.append(bt)
      poses.add(pos)

      for mid in ids.split('/'):
        if mid != '':
          meaning_ids.add(int(mid))

    counter = Counter(backtrans)
    backtrans = counter.most_common(1)[0][0]

    if '' in poses:
      poses.remove('')
    poses = '/'.join(sorted(poses))

    if '' in meaning_ids:
      meaning_ids.remove('')
    meaning_ids = '/'.join(sorted([str(mid) for mid in meaning_ids]))

    combined.append((key[0], key[1], key[2], backtrans, poses, meaning_ids))

  for arr in combined:
    print('\t'.join(arr))


if __name__ == '__main__':
  main()
