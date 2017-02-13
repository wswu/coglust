#!/usr/bin/env python3

import sys

swadesh = []
with open('/export/a08/wwu/res/panlex_swadesh/swadesh110/eng-000.txt') as fin:
  for line in fin:
    for word in line.strip().split('\t'):
      swadesh.append(word)

# remove pronouns
remove = ['1 sg.', '1 pl. inc.', '2 sg', 'I', 'we', 'we₁', 'you', 'thou', 'who', 'who?', 'this', 'that']
swadesh = set(swadesh) - set(remove)
print(swadesh)

with open(sys.argv[1]) as fin:
  for line in fin:
    line = line.strip('\n')
    f, e, lang, bt, pos, mi = line.split('\t')
    if e in swadesh:
      print(line)

