#!/usr/bin/env python3

'''
Create matched files for MEMT. Requires Python 3.6

Usage:
  ~/coglust/memt-parse.py ../cog-exp-romance/exp/dev fra,spa por
  ~/softw/MEMT/MEMT/Alignment/match.sh matched-fra matched-spa > dev.matched
'''

import sys

folder = sys.argv[1]
srcs = sys.argv[2].split(',')
tgt = sys.argv[3]

one_bests = {}
reference = {}

for src in srcs:
  with open(f'{folder}/{src}-{tgt}.idx') as index_file, \
       open(f'{folder}/{src}-{tgt}.out') as out_file, \
       open(f'{folder}/{src}-{tgt}.tgt') as tgt_file:
    for idx_line, out_line, ref_line in zip(index_file, out_file, tgt_file):
      index = int(idx_line.strip())
      one_best = out_line.strip().split(',')[0].split('(')[0]
      one_best = ' '.join(one_best)
      one_bests[(index, src)] = one_best

      reference[index] = ref_line.strip()

indices = sorted(set([idx for idx, src in one_bests]))
for src in srcs:
  with open(f'matched-{src}', 'w') as fout:
    for index in indices:
      one_best = one_bests.get((index, src), '')
      print(one_best, file=fout)

with open('dev.reference', 'w') as fout:
  for index in sorted(reference):
    print(reference[index], file=fout)


