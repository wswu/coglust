#!/usr/bin/env python3

'''
grab lex files and put them in a single folder
'''

import glob
import os
import shutil
import sys

expdir = sys.argv[1]

os.makedirs('lex', exist_ok=True)
for path in glob.glob(expdir + '/models/*/model/lex.f2e'):
    langpair = path.split('/')[-3]
    shutil.copy(path, 'lex/' + langpair)
