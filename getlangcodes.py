#!/usr/bin/env python3

import sqlite3

if __name__ == '__main__':
  conn = sqlite3.connect('/export/a08/wwu/res/panlex_lite/db.sqlite')
  c = conn.cursor()
  command = '''SELECT lv, lc, tt from lv'''

  langs = c.execute(command)
  for row in c.fetchall():
    print('\t'.join([str(x) for x in row]))
