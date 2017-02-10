#!/usr/bin/env python3

import numpy as np
import os

from itertools import groupby, chain
from scipy.cluster.hierarchy import linkage, fcluster
import editdistance

import config
import weightedlev

weights = [0.35, 0.35, 0.1, 0.1, 0.1]

def inter_dist(w1, w2):
  if w1.lang == w2.lang:
    return intra_dist(w1, w2)
  else:
    funcs = weightedlev.load_lex(lex_folder, w1.lang, w2.lang)
    return weightedlev.weightedlev(w1.foreign, w2.foreign, funcs) / (0.5 * (len(w1.foreign) + len(w2.foreign)))

def intra_dist(w1, w2):
  funcs = weightedlev.load_lex(lex_folder, 'AAA', 'BBB')
  return weightedlev.weightedlev(w1.foreign, w2.foreign, funcs) / (0.5 * (len(w1.foreign) + len(w2.foreign)))

def normalized_levenshtein_dist(w1, w2):
  return editdistance.eval(w1.foreign, w2.foreign) / (0.5 * (len(w1.foreign) + len(w2.foreign)))

def weighted_dist(w1, w2):
  features = [
    inter_dist(w1, w2),
    intra_dist(w1, w2),
    0 if w1.backtrans == w2.backtrans else 1,
    0 if len(w1.pos.intersection(w2.pos)) > 0 else 1,
    0 if len(w1.meaning_ids.intersection(w2.meaning_ids)) > 0 else 1
  ]

  #print(w1.foreign + '/' + w1.lang, w2.foreign + '/' + w2.lang, features)
  #print('score', np.inner(features, weights), 'threshold', threshold)

  return np.inner(features, weights)

class Word:
  def __init__(self, foreign, english, lang, backtrans, pos, meaning_ids):
    '''
    meaning_ids is a set
    '''
    self.foreign = foreign
    self.english = english
    self.lang = lang
    self.backtrans = backtrans
    self.pos = pos
    self.meaning_ids = meaning_ids

  def __str__(self):
    return '\t'.join([self.foreign, self.english, self.lang, self.backtrans, self.pos, '/'.join(list(self.meaning_ids))])


def read_combined_table(filename):
  '''
  Reads a table in the format
    foreign \t english \t lang \t backtranslation \t meaningId1/meaningId2/etc
  '''
  with open(filename, encoding='utf-8') as fin:
    words = []
    for line in fin:
      f, e, lang, backtrans, pos, meaning_ids = line.strip('\n').split('\t')
      pos = set(pos.split('/'))
      meaning_ids = set(meaning_ids.split('/'))
      words.append(Word(f, e, lang, backtrans, pos, meaning_ids))
    return words


def cluster(words, linkage_method):
  '''
  distance_func and threshold are global vars!
  '''

  if len(words) == 1:
    clusters = [1]
  else:
    def dist(pair):
      i, j = pair
      return distance_func(words[i], words[j])

    triu = np.triu_indices(len(words), 1)
    distances = np.apply_along_axis(dist, 0, triu)

    linkage_matrix = linkage(distances, method=linkage_method)
    clusters = fcluster(linkage_matrix, threshold, criterion='distance')

  return clusters


def cluster_and_plot(words, linkage_method):
  '''
  distance_func and threshold are global vars!
  '''

  if len(words) == 1:
    clusters = [1]
  else:
    def dist(pair):
      i, j = pair
      return distance_func(words[i], words[j])

    triu = np.triu_indices(len(words), 1)
    print(triu)
    distances = np.apply_along_axis(dist, 0, triu)
    print('distances:', distances)

    for link_method in ['single', 'average', 'complete']:
      linkage_matrix = linkage(distances, method=link_method)
      clusters = fcluster(linkage_matrix, threshold, criterion='distance')

      plot(words, linkage_matrix, link_method, 0.0)

  return clusters


def run(all_words, linkage_method, output_file):
  with open(output_file, 'w') as fout:
    for eng, words in groupby(all_words, key=lambda x: x.english):
      words = list(words)

      cluster_assignments = cluster(words, linkage_method)
      clus_word = sorted(zip(cluster_assignments, words), key=lambda x: x[0])

      for cluster_num, cluster_items in groupby(clus_word, key=lambda x: x[0]):
        this_cluster_words = [word for num, word in cluster_items]
        print(eng + '\t' + '\t'.join([word.foreign + '/' + word.lang for word in this_cluster_words]), file=fout)



import time
from multiprocessing import Pool

def run_par(input_file, output_file):
  start = time.perf_counter()

  words = read_combined_table(input_file)
  os.makedirs(os.path.dirname(output_file), exist_ok=True)

  data = []
  for e, w in groupby(words, key=lambda x: x.english):
    data.append(list(w))

  pool = Pool(8)
  results = pool.map(cluster, data)
  pool.close()
  pool.join()

  with open(output_file, 'w') as fout:
    for line in chain.from_iterable(results):
      fout.write(line)  # already includes newline

  end = time.perf_counter()
  print(end - start)


def make_qsubs(family, thresholds, output_dir):
  for t in thresholds:
    qsub_file = os.path.join(output_dir, 'cluster-{}-{}.sh'.format(family, t))
    os.makedirs(os.path.dirname(qsub_file), exist_ok=True)

    with open('cluster-template.sh') as fin, open(qsub_file, 'w') as out:
      out.write(fin.read()
                   .replace('$ERROR_FILE', qsub_file + '.err')
                   .replace('$FAMILY', family)
                   .replace('$THRESHOLD', t)
                   .replace('$INPUT_FILE', os.path.join(config.exp_dir, 'data', 'gathered'))
                   .replace('$OUTPUT_FILE', os.path.join(config.exp_dir, 'clustered', family + '-' + t)))
    os.system('qsub ' + qsub_file)
    #os.remove(qsub_file)


def plot(words, Z, link_method, _threshold):
  import matplotlib
  matplotlib.use('Agg')
  from matplotlib import pyplot as plt
  from scipy.cluster.hierarchy import dendrogram

  name = 'weighted' if distance_func == weighted_dist else ''

  plt.figure(figsize=(9, 6))
  plt.title(link_method.capitalize() + ' Linkage', fontsize=28)
  #plt.xlabel('distance')
  plt.ylabel('Threshold\n(Normalized ' + name.capitalize() + ' LD)', fontsize=22)
  dendrogram(
    Z,
    #color_threshold=threshold
    #above_threshold_color='#cccccc',
    #orientation='right',
    leaf_rotation=0,  # rotates the x axis labels
    leaf_font_size=20,  # font size for the x axis labels
    leaf_label_func=lambda x: words[x].foreign + '\n(' + words[x].lang + ')'
  )
  #plt.axvline(x=threshold, c='k') # plot threshold line
  plt.savefig('/home/wwu/figures/' + link_method + '-' + name + '.pdf')



def read_args():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('input_file')
  parser.add_argument('distance', help='distance metric "lex" or "unweighted"')
  parser.add_argument('threshold', type=float)
  parser.add_argument('output_file')
  parser.add_argument('--lex', help='folder where .lex files are stored')
  parser.add_argument('--weights', help='weights like 0.1,0.2,0.2,0.3,-0.4')
  parser.add_argument('--plot', action='store_true')
  parser.add_argument('--linkage', help='linkage method for clustering, one of "single", "average", or "complete"')
  return parser.parse_args()

if __name__ == '__main__':
  args = read_args()

  infile = args.input_file
  distance_func = {'lev': normalized_levenshtein_dist, 'weighted': weighted_dist}[args.distance]
  threshold = args.threshold
  lex_folder = args.lex
  output_file = args.output_file
  if args.weights is not None:
    weights = [float(x) for x in args.weights.split(',')]
  if args.plot:
    cluster = cluster_and_plot

  table = read_combined_table(infile)
  table.sort(key=lambda x: x.english)
  run(table, args.linkage, output_file)
