#!/usr/bin/env python3

import os
from itertools import groupby

os.mkdir('multi')
for split in ['train', 'dev', 'test']:
    src = []
    tgt = []
    for langpair, group in groupby(os.listdir('exp/' + split), lambda fname: fname[:7]):
        for f in group:
            srclang, tgtlang = f[:7].split('-')
            if f.endswith('.idx'):
                continue
            elif f.endswith('.src'):
                with open('exp/' + split + '/' + f) as fin:
                    for line in fin:
                        src.append('<' + srclang + '> ' + line.strip() + ' <' + tgtlang + '>')
            elif f.endswith('.tgt'):
                with open('exp/' + split + '/' + f) as fin:
                    for line in fin:
                        tgt.append(line.strip())

    with open('multi/' + split + '.src', 'w') as f:
        for word in src:
            print(word, file=f)
    with open('multi/' + split + '.tgt', 'w') as f:
        for word in tgt:
            print(word, file=f)
