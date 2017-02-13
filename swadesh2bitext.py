#!/usr/bin/env python3

import clustered2bitext

def make_singles():
  for lang in ['eng'] + clustered2bitext.get_langs():
    with open('/export/a08/wwu/res/panlex_swadesh/swadesh110/' + lang + '-000.txt') as fin, \
         open('singles/' + lang, 'w') as singles:
      for line in fin:
        print(line.strip().replace('\t', ','), file=singles)

  clustered2bitext.make_bitext()


if __name__ == '__main__':
  make_singles()
  clustered2bitext.make_bitext()
