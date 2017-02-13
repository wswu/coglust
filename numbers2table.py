#!/usr/bin/env python3

import sys

def format(score):
  return '{:.2f}'.format(float(score)).replace('0.', '.')

with open(sys.argv[1]) as fin:
  print(r'\begin{table}')
  print(r'\begin{tabular}{lrrr}')
  print(r'  \toprule')
  print(r'  ' + fin.readline().strip().replace(',', ' & ') + r' \\')
  print(r'  \midrule')
  for line in fin:
    arr = line.strip().split(',')
    print('  ' + arr[0][arr[0].rfind('/') + 1 :] + ' & ' + ' & '.join([format(score) for score in arr[1:]]) + r' \\')
  print(r'  \bottomrule')
  print(r'\end{tabular}')
  print(r'\end{table}')

with open(sys.argv[1]) as fin:
  data = []
  for line in fin:
    arr = line.strip().split(',')
    data.append(arr)
  data = list(map(list, zip(*data)))

  for row in data[1:]:
    print(row[0] + ' & ' + ' & '.join([format(num) for num in row[1:]]))
