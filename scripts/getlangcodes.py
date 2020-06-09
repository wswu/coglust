'''
Gets the list of language codes and names from PanLex.

Usage: python getlangcodes.py panlex_lite/db.sqlite > langcodes
'''

import sqlite3
import sys
from collections import defaultdict


def main():
    conn = sqlite3.connect(sys.argv[1])
    c = conn.cursor()
    command = 'SELECT lang_code, name_expr_txt from langvar'
    langs = c.execute(command)

    code2names = defaultdict(list)
    for row in c.fetchall():
        code, name = row
        code2names[code].append(name)

    for code in sorted(code2names):
        print(code, ','.join(sorted(code2names[code])))


if __name__ == '__main__':
    main()
