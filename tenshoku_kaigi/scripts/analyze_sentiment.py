#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""analyze sentiment from text data.

Usage:
    analyze_sentiment.py
        --conf_file_path=<conf_file_path>
    analyze_sentiment.py -h | --help
Options:
    -h --help  show this screen and exit.
"""

from datetime import datetime
from docopt import docopt
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import pymysql
import sys
from time import sleep
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

    # google api
    client = language.LanguageServiceClient()

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
        + 'tenshoku_kaigi.analyze_sentiment'\
        + '(word_of_mouth_id, score, magnitude) '\
        + 'VALUES (%s, %s, %s);'

    # select
    tmp = []
    cur.execute(select_sql, company_id)
    mysql_results = cur.fetchall()
    for mysql_result in mysql_results:
        # analyze sentiment
        document = types.Document(
            content=mysql_result[1],
            type=enums.Document.Type.PLAIN_TEXT,
            language='ja'
        )
        sentiment = client.analyze_sentiment(document=document).document_sentiment

        # append
        score = round(sentiment.score, 4)
        magnitude = round(sentiment.magnitude, 4)
        tmp.append([mysql_result[0], score, magnitude])
        sleep(0.5)

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
