#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://analytics.twitter.com ."""

from datetime import datetime
from dateutil.relativedelta import relativedelta
import lxml.html
from lxml.html import HtmlElement
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
from time import sleep
import unittest
from unittest import mock

try:
    import get_data_from_twitter_analytics
except ModuleNotFoundError:
    sys.path.append(os.getcwd() + '/../twitter_analytics')
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
            + 'test'\
            + '</li>'\
            + '<span class="tweet-text">'\
            + '</span>'\
            + '</ul>'\
            + '</body>'\
            + '</html>'
        page_source = lxml.html.fromstring(test_html)
        self.assertEqual(self.gdfta.get_tweets_data(page_source), [])

