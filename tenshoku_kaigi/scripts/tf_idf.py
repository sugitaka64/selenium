#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""word count.

Usage:
    tf_idf.py
        --conf_file_path=<conf_file_path>
        --output_dir_path=<output_dir_path>
    tf_idf.py -h | --help
Options:
    -h --help  show this screen and exit.
"""

from datetime import datetime
from docopt import docopt
import pandas as pd
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import yaml

if __name__ == '__main__':
    print('%s %s start.' % (datetime.today(), __file__))

    # get parameters
    args = docopt(__doc__)
    conf_file_path = args['--conf_file_path']
    output_dir_path = args['--output_dir_path']

    # config
    with open(conf_file_path) as f:
        conf_data = yaml.load(f)
    company_id = conf_data['company_id']
    mysql_host = conf_data['mysql_host']
    mysql_user = conf_data['mysql_user']
    mysql_pw = conf_data['mysql_pw']
    tf_idf_csv_file_path = output_dir_path + 'tf_idf.csv'
    max_tf_idf_csv_file_path = output_dir_path + 'max_tf_idf.csv'

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
    sql = 'SELECT '\
        + 'ma.word_of_mouth_id, ma.word '\
        + 'FROM tenshoku_kaigi.morphological_analysis AS ma '\
        + 'INNER JOIN tenshoku_kaigi.word_of_mouth_comment AS womc '\
        + 'ON ma.word_of_mouth_id = womc.id '\
        + 'WHERE womc.company_id = %s;'

    # select
    word_list = {}
    cur.execute(sql, company_id)
    mysql_results = cur.fetchall()
    for mysql_result in mysql_results:
        # make list
        # ex. tmp[id] = [word_1, word_2, ..., word_n]
        if mysql_result[0] not in word_list:
            word_list[mysql_result[0]] = []

        word_list[mysql_result[0]].append(mysql_result[1])
    cur.close()
    conn.close()

    # make list and mapping for id
    distribution = []
    cnt = 0
    id_index_mapping = {}
    for k, v in word_list.items():
        distribution.append(' '.join(v))
        id_index_mapping[cnt] = k
        cnt += 1
    del(word_list)

    # tf-idf
    vectorizer = TfidfVectorizer(max_df=0.5)
    transformed = vectorizer.fit_transform(distribution)
    del(distribution)

    # make mapping for words
    word_column_mapping = {}
    for k, v in sorted(vectorizer.vocabulary_.items(), key=lambda x: x[1]):
        word_column_mapping[v] = k

    # make data frame
    df = pd.DataFrame(transformed.todense())
    df = df.rename(index=id_index_mapping, columns=word_column_mapping)

    # make csv
    df.to_csv(tf_idf_csv_file_path, index=True, header=True)

    # max value
    max_df = df.max(axis=1)
    idxmax_df = df.idxmax(axis=1)
    df = pd.concat([idxmax_df, max_df], axis=1).rename(columns={0: 'word', 1: 'score'})
    df.to_csv(max_tf_idf_csv_file_path, index=True, header=True)

    print('%s %s end.' % (datetime.today(), __file__))
    sys.exit(0)
