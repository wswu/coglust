#!/usr/bin/env python3

import csv
import functools
import os.path
import sys
from collections import namedtuple
from itertools import groupby

import config
import langcodes
import pycountry


@functools.lru_cache(maxsize=None)
def to3(lang_code):
    try:
        return pycountry.languages.get(iso639_1_code=lang_code).iso639_3_code
    except:
        return None


class Word:
    def __init__(self, foreign, english, lang, pos, meaning_id):
        self.foreign = foreign
        self.english = english
        self.lang = lang
        self.pos = pos
        self.meaning_id = meaning_id
        self.backtrans = ''


def extend_with_microlangs(langs):
    all_langs = list(langs)
    for lang in langs:
        for micro in langcodes.microlangs[lang]:
            all_langs.append(micro)
    return all_langs


def gather_from_wiktionary(langs):
    langs = set(extend_with_microlangs(langs))
    with open(config.wiktionary_location) as fin:
        entries = []
        reader = csv.reader(fin, delimiter='\t', quoting=csv.QUOTE_NONE)
        next(reader, None)  # skip header
        for arr in reader:
            # e, f, en, lang, pos, gender
            if arr[2] == 'en' and to3(arr[3]) in langs:
                entries.append(Word(arr[1].strip(), arr[0].strip(), langcodes.macrolang(to3(arr[3])), arr[4].strip(), None))
            # f, e, lang, en, pos, gender
            elif arr[3] == 'en' and to3(arr[2]) in langs:
                entries.append(Word(arr[0].strip(), arr[1].strip(), langcodes.macrolang(to3(arr[2])), arr[4].strip(), None))
        return entries


def gather_from_panlex(langs):
    langs = extend_with_microlangs(langs)
    entries = []
    for lang in langs:
        filename = config.panlex_location.format(lang)
        if not os.path.isfile(filename):
            continue
        with open(filename) as fin:
            reader = csv.reader(fin)
            next(reader, None)  # skip header
            for f, e, meaning_id, pos in reader:
                entries.append(Word(f.strip(), e.strip(), langcodes.macrolang(lang), None, meaning_id.strip()))  # ignore pos
    return entries


def gather_from_panlex_backtrans(path):
    entries = []
    for lang in os.listdir(path):
        with open(path + '/' + lang) as f:
            reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
            for e, f, backtrans, _trans_score, meaning_ids in reader:
                word = Word(f, e, langcodes.macrolang(lang), None, meaning_ids)
                word.backtrans = backtrans
                entries.append(word)
    return entries


def gather(langs, extra_dicts, output_file, gathered_panlex_path=None):
    wik_words = gather_from_wiktionary(langs)
    print('wiktionary:', len(wik_words))

    if gathered_panlex_path is None:
        pan_words = gather_from_panlex(langs)
    else:
        pan_words = gather_from_panlex_backtrans(gathered_panlex_path)
    print('panlex:', len(pan_words))

    # gather words from extra dictionaries, must be in f \t e \t lang \t pos format
    #  extras = []
    #  for filename in extra_dicts:
    #    with open(filename) as fin:
    #      reader = csv.reader(fin, delimiter='\t', quoting=csv.QUOTE_NONE)
    #      for f, e, lang, pos in reader:
    #        extras.append(Word(f.strip(), e.strip(), langcodes.macrolang(lang), pos.strip(), None))
    #  print('extras:', len(extras))

    # merge results
    combined = wik_words + pan_words #+ extras
    combined = sorted(combined, key=lambda x: (x.english, x.foreign, x.lang))
    with open(output_file, 'w') as fout:
        for key, group in groupby(combined, lambda x: (x.english, x.foreign, x.lang)):
            group = list(group)
            english, foreign, lang = key

            pos = set(normalize_pos(x.pos) for x in group if x.pos is not None and x.pos is not '')

            backtrans = set(x.backtrans for x in group if x != '')
            if '' in backtrans:
                backtrans.remove('')
            if len(backtrans) == 0:
                backtrans = {english}
            if len(backtrans) != 1:
                print('more than one backtrans', backtrans, key)
            backtrans = list(backtrans)[0]

            if backtrans != english:
                print(key, backtrans)

            meaning_id = set(x.meaning_id for x in group if x.meaning_id is not None)


            print(english, foreign, lang, backtrans, '/'.join(pos), '/'.join(meaning_id),
                  sep='\t', file=fout)


def normalize_pos(pos):
    pos = pos.upper()
    if pos == 'ADJECTIVE':
        pos = 'ADJ'
    return pos


def parseargs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('langs_file')
    parser.add_argument('output_file')
    parser.add_argument('--gathered_panlex')
    return parser.parse_args()


def main():
    args = parseargs()
    langs = open(args.langs_file).read().strip().split('\n')
    gather(langs, [], args.output_file, args.gathered_panlex)


if __name__ == '__main__':
    main()
