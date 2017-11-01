#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://analytics.twitter.com .

Usage:
    twitter_analytics.py
        --conf_file_path=<conf_file_path>
        --output_dir_path=<output_dir_path>
    twitter_analytics.py -h | --help

Options:
    -h --help  show this screen and exit.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from docopt import docopt
import os
import pandas as pd
import sys
import yaml

try:
    import get_data_from_twitter_analytics
except ModuleNotFoundError:
    sys.path.append(os.getcwd() + '/twitter_analytics')
    import get_data_from_twitter_analytics

if __name__ == '__main__':
    print('%s %s start.' % (datetime.today(), __file__))

    # get parameters
    args = docopt(__doc__)
    conf_file_path = args['--conf_file_path']
    output_dir_path = args['--output_dir_path']

    # config
    with open(conf_file_path) as f:
        conf_data = yaml.load(f)
    tw_id = conf_data['tw_id']
    tw_pw = conf_data['tw_pw']
    audience_insights_url = conf_data['audience_insights_url']
    tweets_data_csv_file_path = output_dir_path + 'tweets_data.csv'
    attainment_data_csv_file_path = output_dir_path + 'attainment_data.csv'
    audience_insights_data_csv_file_path = output_dir_path + 'audience_insights_data.csv'

    # target month (last month)
    today = datetime.today()
    this_month_start = datetime(today.year, today.month, 1)
    last_month_start = this_month_start + relativedelta(months=-1)
    last_month_end = this_month_start + relativedelta(days=-1)
    last_month_days = (last_month_end - last_month_start).days + 1
    last_month = last_month_start.strftime('%Y%m')

    # create model
    gdfta = get_data_from_twitter_analytics.GetDataFromTwitterAnalytics(tw_id, tw_pw, last_month)

    # get home page soucrce
    page_source = gdfta.get_home_page_source()
    # get home data
    home_data = gdfta.get_home_data(page_source)

    # get tweets page soucrce
    page_source = gdfta.get_tweets_page_source()
    # get tweets data
    tweets_data = gdfta.get_tweets_data(page_source)
    sub_data = gdfta.get_sub_data(page_source)

    # to csv
    # tweets data
    df = pd.DataFrame.from_dict(tweets_data)
    df = df.ix[
        :,
        [
            'twitter_id',
            'tweet',
            'impression',
            'engagement',
            'engagement_percent',
            'target_date',
            'created_at',
        ]
    ]
    df.to_csv(tweets_data_csv_file_path, index=False, header=True)

    # attainment data
    attainment_data = {}
    attainment_data['twitter_id'] = sub_data['twitter_id']
    attainment_data['follower_count'] = home_data['follower_count']
    attainment_data['tweet_count'] = df['tweet'].count()
    attainment_data['engagement_count'] = df['engagement'].sum()
    attainment_data['impression_count'] = df['impression'].sum()
    attainment_data['rt_count'] = sub_data['rt_count']
    attainment_data['fav_count'] = sub_data['fav_count']
    attainment_data['engagement_percent'] = sub_data['engagement_percent']
    attainment_data['impression_count_per_day']\
        = round((attainment_data['impression_count'] / last_month_days), 4)
    attainment_data['rt_count_per_day']\
        = round((attainment_data['rt_count'] / last_month_days), 4)
    attainment_data['fav_count_per_day']\
        = round((attainment_data['fav_count'] / last_month_days), 4)
    attainment_data['created_at'] = sub_data['created_at']
    df = pd.DataFrame.from_dict([attainment_data])
    df = df.ix[
        :,
        [
            'twitter_id',
            'follower_count',
            'tweet_count',
            'engagement_count',
            'impression_count',
            'rt_count',
            'fav_count',
            'engagement_percent',
            'impression_count_per_day',
            'rt_count_per_day',
            'fav_count_per_day',
            'created_at',
        ]
    ]
    df.to_csv(attainment_data_csv_file_path, index=False, header=True)

    # audience insights data
    if audience_insights_url is not None:
        # get audience insights page source
        page_source = gdfta.get_audience_insights_page_source(audience_insights_url)
        # get audience insights data
        audience_insights_data = gdfta.get_audience_insights_data(page_source)

        # to csv
        df = pd.DataFrame.from_dict(audience_insights_data)
        df = df.ix[
            :,
            [
                'twitter_id',
                'category',
                'label',
                'percent',
                'created_at',
            ]
        ]
        df.to_csv(audience_insights_data_csv_file_path, index=False, header=True)

    print('%s %s end.' % (datetime.today(), __file__))
    sys.exit(0)
