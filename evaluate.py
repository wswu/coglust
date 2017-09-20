#!/usr/bin/env python3

'''
This replaces multral/compute_numbers.py
'''

import os
import sys
from itertools import groupby


def load_data(src, gold, output):
    data = []
    with open(src) as fsrc, open(gold) as fgold, open(output) as fout:
        for s, g, o in zip(fsrc, fgold, fout):
            s = s.strip()
            g = g.strip()
            o = o.strip()
            data.append((s, g, o))
    return data


def nlist2list(nlist):
    return [despace(x.split('(')[0]) for x in nlist.split(',')]


def despace(word):
    return word.replace(' ', '').replace('_', ' ')


def acc(data):
    onebest = 0.0
    tenbest = 0.0
    mrr = 0.0
    total = 0.0
    for k, group in groupby(data, lambda x: x[0]):  # src word
        group = list(group)

        golds = set(despace(x[1]) for x in group)
        if len(golds) == 1:  # comma separated, already grouped
            golds = set(list(golds)[0].split(','))

        outs = set(x[2] for x in group)
        assert len(outs) == 1  # should have the same output per input word

        hyps = nlist2list(list(outs)[0])

        if hyps[0] in golds:
            onebest += 1
        if any(x in golds for x in hyps[:10]):
            tenbest += 1
        idx = max(hyps.index(g) if g in hyps else -1 for g in golds)
        mrr += 1.0 / (idx + 1) if idx > -1 else 0

        total += 1
    return onebest / total, tenbest / total, mrr / total


def get_names(path):
    return [x.split('.')[0] for x in os.listdir(path) if x.endswith('.src')]


if __name__ == '__main__':
    path = sys.argv[1]  # folder with test data
    print('Lang', '1best', '10best', 'mrr', sep='\t')
    for f in get_names(path):
        src = path + '/' + f + '.src'
        gold = path + '/' + f + '.tgt'
        out = path + '/' + f + '.out'
        data = load_data(src, gold, out)
        print(f + '\t' + '\t'.join('{:.3f}'.format(x) for x in acc(data)))
