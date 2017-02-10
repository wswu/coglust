#!/usr/bin/env python3

import sqlite3
from collections import Counter
from itertools import groupby


def get_lang_codes_dict():
  langs = {}
  with open('langcodes', encoding='utf-8') as fin:
    for line in fin:
      arr = line.strip().split('\t')
      if arr[1] not in langs:
        langs[arr[0]] = arr[1]
  return langs


if __name__ == '__main__':
#  langs = [382,  # latin
#          211,  # french
#          666,  # spanish
#          579,  # portuguese
#          304,  # italian
#          101,  # catalan
#          610,  # romanian
#  ]
  langs = [738,  # turkish
           54,   # azerbaijani
           759,  # uzbek (north)
           326,  # kazakh
           1832,  # uyghur
           737,  # turkmen
           701,  # tatar
  ]

  conn = sqlite3.connect('/export/a08/wwu/res/panlex_lite/db.sqlite')
  c = conn.cursor()
  command = '''
   SELECT ex.tt, ex2.tt, max(dnx.uq) AS uq, dnx.mn
   FROM dnx
   JOIN ex ON (ex.ex = dnx.ex)
   JOIN dnx dnx2 ON (dnx2.mn = dnx.mn)
   JOIN ex ex2 ON (ex2.ex = dnx2.ex)
   WHERE dnx.ex != dnx2.ex AND ex.lv = 187 AND ex2.lv = XXX
   GROUP BY ex2.tt, dnx.ui
   ORDER BY ex.tt, ex2.tt
   ;
  '''


  lang_name = get_lang_codes_dict()

  for lang in langs:
    c.execute(command.replace('XXX', str(lang)))
    words = c.fetchall()  # eng, word, uq, mn


    backtranslations = {}
    for word, items in groupby(words, key=lambda x: x[1]):
      tr = Counter()
      for eng, items2 in groupby(items, key=lambda x: x[0]):
        for e, f, uq, mn in items2:
          tr[e] += uq
      backtranslations[word] = tr.most_common(1)[0][0]


    with open('dicts/' + lang_name[str(lang)], 'w') as fout:
      for eng_word, items in groupby(words, key=lambda x: (x[0], x[1])):
        english, foreign = eng_word
        items = list(items)
        score = sum([uq for eng, w, uq, mn in items])
        backtrans = backtranslations[foreign]
        meaning_ids = sorted(list(set([mn for eng, w, uq, mn in items])))

        print(english + '\t' +
              foreign + '\t' +
              backtrans + '\t' +
              str(score) + '\t' +
              '/'.join([str(mn) for mn in meaning_ids]),
              file=fout)

  conn.close()
