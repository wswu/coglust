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
  return weightedlev3(s1, s2, cost_funcs[0], cost_funcs[1], cost_funcs[2])


def weightedlev3(s1, s2, ins_cost, del_cost, sub_cost):
  dist = np.zeros((len(s1) + 1, len(s2) + 1))

  for i in range(len(s1) + 1):
    dist[i][0] = i * 1

  for j in range(len(s2) + 1):
    dist[0][j] = j * 1

  for i in range(1, len(s1) + 1):
    for j in range(1, len(s2) + 1):
      dist[i][j] = min(
        dist[i - 1][j] + ins_cost(s1[i - 1]),
        dist[i][j - 1] + del_cost(s2[j - 1]),
        dist[i - 1][j - 1] + sub_cost(s1[i - 1], s2[j - 1]))

  return dist[len(s1), len(s2)]


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


def convert_to_cost_funcs(ins_map, del_map, sub_map):
  def ins_cost(c):
    return ins_map.get(c, 1.0)

  def del_cost(c):
    return del_map.get(c, 1.0)

  def sub_cost(a, b):
    return 0 if a == b else sub_map.get((a, b), 1.0)

  return ins_cost, del_cost, sub_cost


def convert_to_cost_functions(ins_map, del_map, sub_map, identity_sub_cost_zero = False):
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
    vowel = 0.2 if unidecode(a) in Vowels and unidecode(b) in Vowels else 1.0
    identity = 0.0 if a == b else 1.0
    punct = 0.15 if curses.ascii.ispunct(a[0]) and curses.ascii.ispunct(b[0]) else 1.0
    return min(sub, backoff, base, vowel, identity, punct)

  return ins_cost, del_cost, sub_cost


Vowels = set(['a', 'e', 'i', 'o', 'u'])
fallback_ins = { 'h' : 0.5, 'y' : 0.8, 'w' : 0.8 }
fallback_sub = {
    ('t', 'd') : 0.4,
    ('m', 'n') : 0.4,
    ('b', 'p') : 0.4,
    ('f', 'v') : 0.4,
    ('s', 'z') : 0.4,
    ('r', 'l') : 0.4,
    ('k', 'g') : 0.4,
    ('b', 'p') : 0.4,
    ('b', 'v') : 0.4,
    ('f', 'p') : 0.4,
    ('j', 'y') : 0.4,
    ('c', 'x') : 0.4,
    ('c', 'k') : 0.4,
    ('x', 's') : 0.4,
    ('y', 'u') : 0.4,
    ('y', 'w') : 0.4,
    ('w', 'u') : 0.4,
    ('q', 'k') : 0.4,
    ('q', 'c') : 0.4,
    ('h', 'j') : 0.4,
    ('h', 'g') : 0.5,
    ('c', 's') : 0.5,

    ('d', 't') : 0.4,
    ('n', 'm') : 0.4,
    ('p', 'b') : 0.4,
    ('v', 'f') : 0.4,
    ('z', 's') : 0.4,
    ('l', 'r') : 0.4,
    ('g', 'k') : 0.4,
    ('p', 'b') : 0.4,
    ('v', 'b') : 0.4,
    ('p', 'f') : 0.4,
    ('y', 'j') : 0.4,
    ('x', 'c') : 0.4,
    ('k', 'c') : 0.4,
    ('s', 'x') : 0.4,
    ('u', 'y') : 0.4,
    ('w', 'y') : 0.4,
    ('u', 'w') : 0.4,
    ('k', 'q') : 0.4,
    ('c', 'q') : 0.4,
    ('j', 'h') : 0.4,
    ('g', 'h') : 0.5,
    ('s', 'c') : 0.5
}


if __name__ == '__main__':
  i, d, s = read_lex_file('/export/a08/wwu/lex-files/turkic/uzn-uig.e2f')
  fi, fd, fs = convert_to_cost_functions(i, d, s)
  print(fi('a'))
  print(fd('b'))
  print(fs('b', 'b'))
