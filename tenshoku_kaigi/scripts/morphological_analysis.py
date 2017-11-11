#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""morphological analysis.

Usage:
    morphological_analysis.py
        --conf_file_path=<conf_file_path>
    morphological_analysis.py -h | --help
Options:
    -h --help  show this screen and exit.
"""

from datetime import datetime
from docopt import docopt
import MeCab
import pymysql
import sys
import yaml

if __name__ == '__main__':
    print('%s %s start.' % (datetime.today(), __file__))

    # get parameters
    args = docopt(__doc__)
    conf_file_path = args['--conf_file_path']

    # config
    with open(conf_file_path) as f:
        conf_data = yaml.load(f)
    company_id = conf_data['company_id']
    mysql_host = conf_data['mysql_host']
    mysql_user = conf_data['mysql_user']
    mysql_pw = conf_data['mysql_pw']

    # mecab tagger
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    # mysql connect
    conn = pymysql.connect(
        host=mysql_host,
        unix_socket='/tmp/mysql.sock',
        user=mysql_user,
        passwd=mysql_pw,
        db='mysql',
        charset='utf8'
    )
    cur = conn.cursor()

    # sql
    select_sql = 'SELECT '\
        + 'id, comment '\
        + 'FROM tenshoku_kaigi.word_of_mouth '\
        + 'WHERE company_id = %s;'
    insert_sql = 'INSERT INTO '\
        + 'tenshoku_kaigi.morphological_analysis'\
        + '(word_of_mouth_id, word) '\
        + 'VALUES (%s, %s);'

    # select
    tmp = []
    cur.execute(select_sql, company_id)
    mysql_results = cur.fetchall()
    for mysql_result in mysql_results:
        # morphological analysis
        mecab_results = tagger.parse(mysql_result[1]).split('\n')
        for mecab_result in mecab_results:
            # EOS
            if mecab_result == 'EOS' or mecab_result == '':
                continue

            # check word class
            mecab_data = mecab_result.split('\t')
            if not mecab_data[1].startswith('名詞,'):
                continue
            if len(mecab_data[0]) <= 1:
                continue
            tmp.append([mysql_result[0], mecab_data[0]])

    # insert
    try:
        cur.executemany(insert_sql, tmp)
    except Exception as e:
        print(e)
        conn.rollback()
        cur.close()
        conn.close()
        sys.exit(1)

    conn.commit()
    cur.close()
    conn.close()

    print('%s %s end.' % (datetime.today(), __file__))
    sys.exit(0)
