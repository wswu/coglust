#!/usr/bin/env python3

'''
pretty print lex file for slides
'''

import sys

data = []
with open(sys.argv[1]) as f:
    for line in f:
        e, f, prob = line.strip().split(' ')
        data.append((f, e, float(prob)))

for f, e, prob in sorted(data, key=lambda x: (x[0], -x[2])):
    print(f'{f} -> {e}  {prob:.3f}')
