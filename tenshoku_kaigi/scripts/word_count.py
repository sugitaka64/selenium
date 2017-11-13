#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""word count.

Usage:
    word_count.py
        --conf_file_path=<conf_file_path>
        --output_dir_path=<output_dir_path>
    word_count.py -h | --help
Options:
    -h --help  show this screen and exit.
"""

from datetime import datetime
from docopt import docopt
import pandas as pd
import pymysql
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
    csv_file_path = output_dir_path + 'word_count.csv'

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
        + 'INNER JOIN tenshoku_kaigi.word_of_mouth AS wom '\
        + 'ON ma.word_of_mouth_id = wom.id '\
        + 'WHERE wom.company_id = %s;'

    # select
    tmp = {}
    cur.execute(sql, company_id)
    mysql_results = cur.fetchall()
    for mysql_result in mysql_results:
        # word count
        # ex. tmp[id][word] = count
        if mysql_result[0] not in tmp:
            tmp[mysql_result[0]] = {}
        if mysql_result[1] not in tmp[mysql_result[0]]:
            tmp[mysql_result[0]][mysql_result[1]] = 1
        else:
            tmp[mysql_result[0]][mysql_result[1]] += 1

    cur.close()
    conn.close()

    # make csv
    df = pd.DataFrame.from_records(tmp).fillna(0.0).T
    df.to_csv(csv_file_path, index=True, header=True)

    print('%s %s end.' % (datetime.today(), __file__))
    sys.exit(0)
