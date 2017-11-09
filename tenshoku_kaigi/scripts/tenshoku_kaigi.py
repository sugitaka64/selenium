#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://jobtalk.jp/ .

Usage:
    tenshoku_kaigi.py
        --conf_file_path=<conf_file_path>
        --output_dir_path=<output_dir_path>
    tenshoku_kaigi.py -h | --help
Options:
    -h --help  show this screen and exit.
"""

from datetime import datetime
from docopt import docopt
import os
import pandas as pd
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
    output_dir_path = args['--output_dir_path']

    # config
    with open(conf_file_path) as f:
        conf_data = yaml.load(f)
    login_id = conf_data['login_id']
    login_pw = conf_data['login_pw']
    company_id = conf_data['company_id']
    reputations_data_csv_file_path = output_dir_path + 'reputations_data.csv'
    salaries_data_csv_file_path = output_dir_path + 'salaries_data.csv'
    exams_data_csv_file_path = output_dir_path + 'exams_data.csv'

    # create model
    gdftk = get_data_from_tenshoku_kaigi.GetDataFromTenshokuKaigi(login_id, login_pw, company_id)

    # get reputations data
    reputations_data = gdftk.get_reputations_data()
    salaries_data = gdftk.get_salaries_data()
    exams_data = gdftk.get_exams_data()

    # to csv
    # reputations data
    for dict_data in [
        [reputations_data, reputations_data_csv_file_path],
        [salaries_data, salaries_data_csv_file_path],
        [exams_data, exams_data_csv_file_path],
    ]:
        df = pd.DataFrame.from_dict(dict_data[0])
        df = df.ix[
            :,
            [
                'comment',
                'raiting',
                'review_id',
                'post_date',
                'created_at',
            ]
        ]
        df.to_csv(dict_data[1], index=False, header=True)

    print('%s %s end.' % (datetime.today(), __file__))
    sys.exit(0)
