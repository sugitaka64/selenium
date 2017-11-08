#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://analytics.twitter.com ."""

from datetime import datetime
from dateutil.relativedelta import relativedelta
import lxml.html
from lxml.html import HtmlElement
import os
import sys
import unittest
from unittest import mock

try:
    import get_data_from_twitter_analytics
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../twitter_analytics')
    import get_data_from_twitter_analytics

class GetDataFromTwitterAnalyticsTests(unittest.TestCase):
    """get data from https://analytics.twitter.com ."""

    def setUp(self):
        """set up."""
        self.tw_id = 'id'
        today = datetime.today()
        this_month_start = datetime(today.year, today.month, 1)
        last_month_start = this_month_start + relativedelta(months=-1)
        self.last_month = last_month_start.strftime('%Y%m')

        # create model
        self.gdfta = get_data_from_twitter_analytics.GetDataFromTwitterAnalytics(
            self.tw_id,
            'pw',
            self.last_month,
        )

        # set mock
        test_html = '<html><body>test</body></html>'
        self.gdfta.driver.get = mock.Mock()
        self.gdfta.driver.get.return_value = test_html
        self.gdfta.driver.find_element_by_css_selector = mock.Mock()
        self.gdfta.driver.find_element_by_css_selector.click = mock.Mock()
        self.gdfta.driver.find_element_by_css_selector.click.return_value = True
        self.gdfta.driver.find_elements_by_xpath = mock.Mock()
        self.gdfta.driver.find_elements_by_xpath.return_value = [mock.Mock()]
        self.gdfta.driver.find_elements_by_xpath.click = mock.Mock()
        self.gdfta.driver.find_elements_by_xpath.click.return_value = True

    def test_init(self):
        """init."""
        self.assertEqual(self.gdfta.tw_id, self.tw_id)
        self.assertEqual(self.gdfta.target_month, self.last_month)
        self.assertTrue(isinstance(self.gdfta.driver.page_source, str))

    def test_get_home_page_source(self):
        """get home page source."""
        self.assertTrue(isinstance(self.gdfta.get_home_page_source(), HtmlElement))

    def test_get_tweets_page_source(self):
        """get tweets page source."""
        self.assertTrue(isinstance(self.gdfta.get_tweets_page_source(), HtmlElement))

    def test_get_audience_insights_page_source(self):
        """get tweets page source."""
        test_html = '<html><body>test</body></html>'
        audience_insights_url = 'test'

        self.gdfta.driver.get = mock.Mock()
        self.gdfta.driver.get.return_value = test_html

        self.assertTrue(
            isinstance(
                self.gdfta.get_audience_insights_page_source(audience_insights_url),
                HtmlElement
            )
        )

    def test_get_home_data(self):
        """get home data."""
        test_html = '<html><body>test</body></html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_home_data(page_source), {})

        test_html_fmt = '<html>'\
            + '<body>'\
            + '<div class="home-summary-panel">'\
            + '<div class="home-summary-metric">'\
            + '<div class="DataPoint-info">'\
            + '%s'\
            + '</div>'\
            + '</div>'\
            + '</div>'\
            + '</body>'\
            + '</html>'

        test_html = test_html_fmt % ('1')
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_home_data(page_source), {'follower_count': 1})

        test_html = test_html_fmt % ('1,000')
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_home_data(page_source), {'follower_count': 1000})

    def test_get_tweets_data(self):
        """get tweets data."""
        test_html = '<html><body>test</body></html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_tweets_data(page_source), [])

        test_html = '<html>'\
            + '<body>'\
            + '<ul>'\
            + '<li class="tweet-stats">'\
            + 'test'\
            + '</li>'\
            + '</ul>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_tweets_data(page_source), [])

        test_html = '<html>'\
            + '<body>'\
            + '<ul>'\
            + '<li class="tweet-stats">'\
            + '<span class="tweet-text">'\
            + 'test'\
            + '</span>'\
            + '</li>'\
            + '</ul>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_tweets_data(page_source), [])

        test_html = '<html>'\
            + '<body>'\
            + '<ul>'\
            + '<li class="tweet-stats">'\
            + '<div class="tweet-activity-data">'\
            + '0'\
            + '</div>'\
            + '</li>'\
            + '</ul>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_tweets_data(page_source), [])

        test_html = '<html>'\
            + '<body>'\
            + '<ul>'\
            + '<li class="tweet-stats">'\
            + '<span class="tweet-text">'\
            + 'test'\
            + '</span>'\
            + '<div class="tweet-activity-data">'\
            + '0'\
            + '</div>'\
            + '<div class="tweet-activity-data">'\
            + '1,000'\
            + '</div>'\
            + '<div class="tweet-activity-data">'\
            + '30%'\
            + '</div>'\
            + '</li>'\
            + '</ul>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        expected_value = [
            {
                'twitter_id': self.tw_id,
                'tweet': 'test',
                'impression': 0,
                'engagement': 1000,
                'engagement_percent': 0.3000,
                'target_date': self.last_month,
            },
        ]
        actual_value = self.gdfta.get_tweets_data(page_source)
        del(actual_value[0]['created_at'])
        self.assertEqual(actual_value, expected_value)

    def test_get_sub_data(self):
        """get rt fav count."""
        test_html = '<html><body>test</body></html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_sub_data(page_source), {})

        test_html = '<html>'\
            + '<body>'\
            + '<div id="engagements-time-series-container">'\
            + '<div class="time-series-value">'\
            + '30%'\
            + '</div>'\
            + '</div>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_sub_data(page_source), {})

        test_html = '<html>'\
            + '<body>'\
            + '<div id="engagements-time-series-container">'\
            + '<div class="time-series-value">'\
            + '30%'\
            + '</div>'\
            + '</div>'\
            + '<div id="clicks-time-series-container">'\
            + '<div class="time-series-value">'\
            + '100'\
            + '</div>'\
            + '</div>'\
            + '<div id="retweets-time-series-container">'\
            + '<div class="time-series-value">'\
            + '1,000'\
            + '</div>'\
            + '</div>'\
            + '<div id="favs-time-series-container">'\
            + '<div class="time-series-value">'\
            + '100'\
            + '</div>'\
            + '</div>'\
            + '<div id="replies-time-series-container">'\
            + '<div class="time-series-value">'\
            + '1,000'\
            + '</div>'\
            + '</div>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        expected_value = {
            'twitter_id': self.tw_id,
            'engagement_percent': 0.3000,
            'link_click_count': 100,
            'rt_count': 1000,
            'fav_count': 100,
            'reply_count': 1000,
            'target_date': self.last_month,
        }
        actual_value = self.gdfta.get_sub_data(page_source)
        del(actual_value['created_at'])
        self.assertEqual(actual_value, expected_value)

    def test_get_audience_insights_data(self):
        """get audience insights data."""
        test_html = '<html><body>test</body></html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_audience_insights_data(page_source), [])

        test_html = '<html>'\
            + '<body>'\
            + '<div class="demographics">'\
            + '<div class="vertical-bar-panel">'\
            + 'test'\
            + '</div>'\
            + '<div class="top-n-panel">'\
            + 'test'\
            + '</div>'\
            + '</div>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_audience_insights_data(page_source), [])

        test_html = '<html>'\
            + '<body>'\
            + '<div class="demographics">'\
            + '  <div class="vertical-bar-panel">'\
            + '    <div class="vertical-bar-panel-header">'\
            + '      <h3>'\
            + '        category'\
            + '      </h3>'\
            + '    </div>'\
            + '    <div class="vertical-bar-chart-legend">'\
            + '      <div class="vertical-bar-label">'\
            + '        test'\
            + '      </div>'\
            + '    </div>'\
            + '  </div>'\
            + '  <div class="top-n-panel">'\
            + '    <div class="top-n-panel-header">'\
            + '      <h3>'\
            + '        category'\
            + '      </h3>'\
            + '    </div>'\
            + '    <div class="top-n-panel-table">'\
            + '      <table>'\
            + '        <tbody>'\
            + '          <tr>'\
            + '            test'\
            + '          </tr>'\
            + '        </tbody>'\
            + '      </table>'\
            + '    </div>'\
            + '  </div>'\
            + '</div>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_audience_insights_data(page_source), [])

        test_html = '<html>'\
            + '<body>'\
            + '<div class="demographics">'\
            + '  <div class="vertical-bar-panel">'\
            + '    <div class="vertical-bar-panel-header">'\
            + '      <h3>category_1</h3>'\
            + '    </div>'\
            + '    <div class="vertical-bar-chart-legend">'\
            + '      <div class="vertical-bar-label">'\
            + '        <h6>label_1</h6>'\
            + '        <h4>98%</h4>'\
            + '      </div>'\
            + '    </div>'\
            + '  </div>'\
            + '  <div class="top-n-panel">'\
            + '    <div class="top-n-panel-header">'\
            + '      <h3>category_2</h3>'\
            + '    </div>'\
            + '    <div class="top-n-panel-table">'\
            + '      <table>'\
            + '        <tbody>'\
            + '          <tr>'\
            + '            <td class="top-n-panel-name"><span>label_2</span></td>'\
            + '            <td class="statistic-cell"><span>< 1%</span></td>'\
            + '          </tr>'\
            + '        </tbody>'\
            + '      </table>'\
            + '    </div>'\
            + '  </div>'\
            + '</div>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        expected_value = [
            {
                'twitter_id': self.tw_id,
                'category': 'category_1',
                'label': 'label_1',
                'percent': 0.98,
                'target_date': self.last_month,
            },
            {
                'twitter_id': self.tw_id,
                'category': 'category_2',
                'label': 'label_2',
                'percent': 0.01,
                'target_date': self.last_month,
            },
        ]
        actual_value = self.gdfta.get_audience_insights_data(page_source)
        del(actual_value[0]['created_at'])
        del(actual_value[1]['created_at'])
        self.assertEqual(actual_value, expected_value)
