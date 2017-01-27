#!/usr/bin/env python3

import sys

def good_char(x):
  return x.isalpha() #or x.isspace()

if __name__ == '__main__':
  with open(sys.argv[1]) as fin:
    for line in fin:
      arr = line.strip('\n').split('\t')
      if not all(x.isupper() for x in arr[0]) and all(good_char(x) for x in arr[0]):
        print(line.strip('\n'))
