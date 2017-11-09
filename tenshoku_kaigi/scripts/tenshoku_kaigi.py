#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://jobtalk.jp/ .

Usage:
    tenshoku_kaigi.py
        --conf_file_path=<conf_file_path>
    tenshoku_kaigi.py -h | --help
Options:
    -h --help  show this screen and exit.
"""

from datetime import datetime
from docopt import docopt
import os
import pymysql
import sys
import yaml

try:
    import get_data_from_tenshoku_kaigi
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../tenshoku_kaigi')
    import get_data_from_tenshoku_kaigi

if __name__ == '__main__':
    print('%s %s start.' % (datetime.today(), __file__))

    # get parameters
    args = docopt(__doc__)
    conf_file_path = args['--conf_file_path']

    # config
    with open(conf_file_path) as f:
        conf_data = yaml.load(f)
    login_id = conf_data['login_id']
    login_pw = conf_data['login_pw']
    company_id = conf_data['company_id']
    mysql_host = conf_data['mysql_host']
    mysql_user = conf_data['mysql_user']
    mysql_pw = conf_data['mysql_pw']

    # create model
    gdftk = get_data_from_tenshoku_kaigi.GetDataFromTenshokuKaigi(login_id, login_pw, company_id)

    # get reputations data
    reputations_data = gdftk.get_reputations_data()
    salaries_data = gdftk.get_salaries_data()
    exams_data = gdftk.get_exams_data()

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

    # inset
    sql = 'INSERT INTO '\
        + 'tenshoku_kaigi.word_of_mouth(comment, raiting, review_id, post_date, created_at) '\
        + 'VALUES (%s, %s, %s, %s, %s);'
    for dict_data in [reputations_data, salaries_data, exams_data]:
        for row in dict_data:
            try:
                cur.execute(
                    sql,
                    (
                        row['comment'],
                        row['raiting'],
                        row['review_id'],
                        row['post_date'],
                        row['created_at'],
                    )
                )
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
