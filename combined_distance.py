#!/usr/bin/env python3

'''
Average distance between all words in a language
(Sum up the distances for each cognate and then take the average)
'''

from collections import defaultdict
import sys

#import cluster
import editdistance

def main():
  with open(sys.argv[1]) as fin:
    lang_dist = defaultdict(float)
    counts = defaultdict(int)

    for line in fin:
      arr = line.strip().split('\t')
      # english = arr[0]
      words = [word.split('/') for word in arr[1:]]
      for word1, lang1 in words:
        for word2, lang2 in words:
          if word1 != word2 and lang1 != lang2:
            dist = editdistance.eval(word1, word2)
            lang_dist[(lang1, lang2)] += dist
            lang_dist[(lang2, lang1)] += dist
            counts[(lang1, lang2)] += 1
            counts[(lang2, lang1)] += 1

    for lang_pair in lang_dist:
      lang_dist[lang_pair] /= counts[lang_pair]

    plot(lang_dist)


def read_distances(filename):
  with open(filename) as fin:
    lang_dist = {}
    fin.readline()  # skip header
    for line in fin:
      arr = line.strip().split(',')
      pair = arr[0].split('-')
      dist = float(arr[1])
      lang_dist[(pair[0], pair[1])] = dist
    return lang_dist


def plot(lang_dist):
  langs = list(set(lang for lang, _ in lang_dist))

  import matplotlib
  matplotlib.use('Agg')
  from matplotlib import pyplot as plt
  from scipy.cluster.hierarchy import dendrogram, linkage
  import numpy as np

  def dist(pair):
    x, y = pair
    return lang_dist[(langs[x], langs[y])]

  triu = np.triu_indices(len(langs), 1)
  distances = np.apply_along_axis(dist, 0, triu)
  linkage_matrix = linkage(distances, method='single')

  plt.figure(figsize=(8,5))
  plt.title('Average Distance Per Word (Single Linkage)', fontsize=24)

  dendrogram(
      linkage_matrix,
      leaf_label_func=lambda x: langs[x],
      leaf_font_size=20)
  plt.savefig('/home/wwu/figures/gray-and-atkinson.pdf')


if __name__ == '__main__':
  #main()
  plot(read_distances('gray-and-atkinson'))
