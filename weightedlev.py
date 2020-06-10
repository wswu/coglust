import curses.ascii
import numpy as np
import os.path
from functools import lru_cache
from unidecode import unidecode


@lru_cache(maxsize=None)
def load_lex(lex_folder, src, tgt):
    filename = '{}/{}-{}.f2e'.format(lex_folder, src, tgt)
    if not os.path.isfile(filename):
        print('None!' + filename)
        return None

    i, d, s = read_lex_file(filename)
    fi, fd, fs = convert_to_cost_funcs(i, d, s)
    return fi, fd, fs


def weightedlev(s1, s2, cost_funcs):
    return distance_f(s1, s2, cost_funcs[0], cost_funcs[1], cost_funcs[2])


def read_lex_file(filename):
    with open(filename, encoding='utf-8') as fin:
        ins_map = {}
        del_map = {}
        sub_map = {}
        for line in fin:
            arr = line.strip().split()  # e f p(e|f)
            if arr[1] == 'NULL':
                ins_map[arr[0]] = 1 - float(arr[2])
            elif arr[0] == 'NULL':
                del_map[arr[1]] = 1 - float(arr[2])
            else:
                sub_map[(arr[1], arr[0])] = 1 - float(arr[2])
        return ins_map, del_map, sub_map


def distance(s1, s2, ins_cost={}, del_cost={}, sub_cost={}):
    dist = np.zeros((len(s1) + 1, len(s2) + 1))
    for i in range(len(s1) + 1):
        dist[i][0] = i
    for j in range(len(s2) + 1):
        dist[0][j] = j
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            dist[i][j] = min(
                dist[i][j - 1] + ins_cost.get(s1[i - 1], 1),
                dist[i - 1][j] + del_cost.get(s2[j - 1], 1),
                dist[i - 1][j - 1] + sub_cost.get((s1[i - 1], s2[j - 1]), 0 if s1[i - 1] == s2[j - 1] else 1))
    return dist[len(s1), len(s2)]


def distance_f(s1, s2, ins_cost, del_cost, sub_cost):
    dist = np.zeros((len(s1) + 1, len(s2) + 1))
    for i in range(len(s1) + 1):
        dist[i][0] = i * 1
    for j in range(len(s2) + 1):
        dist[0][j] = j * 1
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            dist[i][j] = min(
                dist[i][j - 1] + ins_cost(s1[i - 1]),
                dist[i - 1][j] + del_cost(s2[j - 1]),
                dist[i - 1][j - 1] + sub_cost(s1[i - 1], s2[j - 1]))
    return dist[len(s1), len(s2)]


def convert_to_cost_funcs(ins_map, del_map, sub_map):
    def ins_cost(c):
        return ins_map.get(c, 1.0)

    def del_cost(c):
        return del_map.get(c, 1.0)

    def sub_cost(a, b):
        return 0 if a == b else sub_map.get((a, b), 1.0)

    return ins_cost, del_cost, sub_cost


def convert_to_cost_functions(ins_map, del_map, sub_map, identity_sub_cost_zero=False):
    def ins_cost(uc):
        c = uc.lower()
        ins = ins_map.get(c, 1.0)
        vowel = 0.2 if unidecode(c) in Vowels else 1.0
        backoff = fallback_ins.get(c, 1.0)
        punct = 0.15 if curses.ascii.ispunct(c[0]) else 1.0
        return min(ins, vowel, backoff, punct)

    def del_cost(uc):
        c = uc.lower()
        del_ = del_map.get(c, 1.0)
        vowel = 0.2 if unidecode(c) in Vowels else 1.0
        punct = 0.15 if curses.ascii.ispunct(c[0]) else 1.0
        return min(del_, vowel, punct)

    def sub_cost(ua, ub):
        a = ua.lower()
        b = ub.lower()
        sub = sub_map.get((a, b), 1.0)
        backoff = fallback_sub.get((a, b), 1.0)
        base = 0.05 if unidecode(a) == unidecode(b) else 1.0
        vowel = 0.2 if unidecode(
            a) in Vowels and unidecode(b) in Vowels else 1.0
        identity = 0.0 if a == b else 1.0
        punct = 0.15 if curses.ascii.ispunct(
            a[0]) and curses.ascii.ispunct(b[0]) else 1.0
        return min(sub, backoff, base, vowel, identity, punct)

    return ins_cost, del_cost, sub_cost


Vowels = set(['a', 'e', 'i', 'o', 'u'])
fallback_ins = {x: 0.2 for x in Vowels}
fallback_ins.update({'h': 0.5, 'y': 0.8, 'w': 0.8})
fallback_del = fallback_ins
CloseSubs = ['td', 'mn', 'bp', 'fv', 'sz', 'rl', 'kg', 'bp', 'bv', 'fp',
             'jy', 'cx', 'ck', 'xs', 'yu', 'yw', 'wu', 'qk', 'qc', 'hj', 'hg']
fallback_sub = {(x[0], x[1]): 0.4 for x in CloseSubs}
fallback_sub.update({(x[1], x[0]): 0.4 for x in CloseSubs})
fallback_sub.update({x: 0.5 for x in ['gh', 'hg', 'cs', 'sc']})


def main():
    # i, d, s = read_lex_file('/export/a08/wwu/lex-files/turkic/uzn-uig.e2f')
    # fi, fd, fs = convert_to_cost_functions(i, d, s)
    # print(fi('a'))
    # print(fd('b'))
    # print(fs('b', 'b'))

    print(distance('winston', 'einstein',
                   del_cost=fallback_del, sub_cost=fallback_sub))


if __name__ == '__main__':
    main()
