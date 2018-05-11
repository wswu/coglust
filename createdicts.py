#!/usr/bin/env python3

import sqlite3

from collections import Counter
from itertools import groupby


def get_lang_codes_dict():
    langs = {}
    with open('/home/wwu/coglust/langcodes', encoding='utf-8') as fin:
        for line in fin:
            arr = line.strip().split('\t')
            if arr[1] not in langs:
                langs[arr[0]] = arr[1]
    return langs

lang_name = get_lang_codes_dict()

command = '''
    SELECT expr.txt, expr2.txt, max(denotationx.quality) as quality, denotationx.meaning
    FROM denotationx
    JOIN expr ON (expr.id = denotationx.expr)
    JOIN denotationx denotationx2 ON (denotationx2.meaning = denotationx.meaning)
    JOIN expr expr2 ON (expr2.id = denotationx2.expr)
    WHERE denotationx.expr != denotationx2.expr AND expr.langvar = 187 AND expr2.langvar = XXX
    GROUP BY expr2.txt
    ORDER BY expr2.txt
    ;
    '''

def run(lang):
    print('lang ', lang, lang_name[lang])

    conn = sqlite3.connect('/export/a08/wwu/res/panlex_lite/db.sqlite', check_same_thread=False)
    c = conn.cursor()
    c.execute(command.replace('XXX', str(lang)))
    words = c.fetchall()  # eng, foreign, tr quality, meaning id

    backtranslations = {}
    for foreign, items in groupby(words, key=lambda x: x[1]):
        tr = Counter()
        for eng, items2 in groupby(items, key=lambda x: x[0]):
            for e, f, uq, mn in items2:
                tr[e] += uq
        backtranslations[foreign] = tr.most_common(1)[0][0]


    with open('/export/a08/wwu/dicts/' + lang_name[str(lang)], 'w') as fout:
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

def makeqsubs():
    num_jobs = 0
    for i, lang in enumerate(lang_name):
        num_jobs += 1
        with open(f'qsubs/{i + 1}', 'w') as f:
            print(f'~/coglust/createdicts.py {lang}', file=f)

    with open('createdicts.sh', 'w') as f:
        print('''
#$ -l mem_free=1G,ram_free=1G
#$ -V
#$ -cwd
#$

source /home/wwu/softw/anaconda3/bin/activate py36

./createdicts.py
''', file=f)

if __name__ == '__main__':
    for langcode in lang_name:
        run(langcode)
    # langs = [382,  # latin
    #         211,  # french
    #         666,  # spanish
    #         579,  # portuguese
    #         304,  # italian
    #         101,  # catalan
    #         610,  # romanian
    # ]
    # langs = [738,  # turkish
    #         54,   # azerbaijani
    #         759,  # uzbek (north)
    #         326,  # kazakh
    #         1832,  # uyghur
    #         737,  # turkmen
    #         701,  # tatar
    # ]
