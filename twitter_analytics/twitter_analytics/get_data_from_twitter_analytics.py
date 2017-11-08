#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://analytics.twitter.com ."""

from datetime import datetime
import lxml.html
from lxml.html import HtmlElement
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep

class GetDataFromTwitterAnalytics(object):
    """get data from https://analytics.twitter.com ."""

    def __init__(
        self,
        tw_id: str,
        tw_pw: str,
        target_month: str,
    ):
        """init."""
        self.tw_id = tw_id
        self.target_month = target_month
        self.today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        # set url
        login_url = 'https://twitter.com/login?redirect_after_login=' \
            + 'https%3A%2F%2Fanalytics.twitter.com'

        # UA
        des_cap = dict(DesiredCapabilities.PHANTOMJS)
        des_cap['phantomjs.page.settings.userAgent'] = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
        )

        # set driver
        self.driver = webdriver.PhantomJS(desired_capabilities=des_cap)

        # login
        self.driver.get(login_url)
        tw_id_form = self.driver.find_element_by_css_selector('form input.js-username-field')
        tw_pw_form = self.driver.find_element_by_css_selector('form input.js-password-field')
        tw_id_form.send_keys(self.tw_id)
        tw_pw_form.send_keys(tw_pw)
        self.driver.find_element_by_css_selector('button.submit').click()

    def get_home_page_source(
        self,
    ) -> HtmlElement:
        """get home page source."""
        # set url
        home_url = 'https://analytics.twitter.com/user/%s/home' % (self.tw_id)

        # access /user/xxx/home
        self.driver.get(home_url)
        sleep(3)

        # get page soucrce
        page_source = lxml.html.fromstring(self.driver.page_source)

        return page_source

    def get_tweets_page_source(
        self,
    ) -> HtmlElement:
        """get tweets page source."""
        # set url
        tweets_url = 'https://analytics.twitter.com/user/%s/tweets' % (self.tw_id)

        # access /user/xxx/tweets
        self.driver.get(tweets_url)

        # set target month
        self.driver\
            .find_element_by_css_selector('div.main-page-header div.daterange-button')\
            .click()
        target_month_label = datetime.strptime(self.target_month, '%Y%m').strftime('%B %Y')
        xpath = '//ul/li[contains(text(), \'%s\')]' % (target_month_label)
        self.driver.find_elements_by_xpath(xpath)[0].click()
        sleep(3)

        # scroll to get last tweets
        scroll_count = 0
        while scroll_count < 5:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(3)
            scroll_count += 1

        # get page soucrce
        page_source = lxml.html.fromstring(self.driver.page_source)

        return page_source

    def get_audience_insights_page_source(
        self,
        audience_insights_url: str,
    ) -> HtmlElement:
        """get tweets page source."""
        # access /accounts/yyy/audience_insights
        self.driver.get(audience_insights_url)
        sleep(3)

        # get page soucrce
        page_source = lxml.html.fromstring(self.driver.page_source)

        return page_source

    def get_home_data(
        self,
        page_source: str,
    ) -> list:
        """get home data."""
        followers = page_source\
            .cssselect('div.home-summary-panel div.home-summary-metric div.DataPoint-info')
        # check data
        if len(followers) == 0:
            return {}

        # get data
        follower = int(followers[-1].text.strip().replace(',', ''))

        home_data = {
            'follower_count': follower,
        }

        return home_data

    def get_tweets_data(
        self,
        page_source: str,
    ) -> list:
        """get tweets data."""
        tweets_data = []
        tweet_statuses = page_source.cssselect('li.tweet-stats')
        for tweet_status in tweet_statuses:
            tweets = tweet_status.cssselect('span.tweet-text')
            activity_data = tweet_status.cssselect('div.tweet-activity-data')
            # check data
            if (
                (len(tweets) != 1) or
                (len(activity_data) != 3)
            ):
                continue
            # get data
            tweet = tweets[0].text_content().strip()
            impression = int(activity_data[0].text.strip().replace(',', ''))
            engagement = int(activity_data[1].text.strip().replace(',', ''))
            engagement_percent = activity_data[2].text.strip()
            engagement_percent = round((float(engagement_percent.replace('%', '')) / 100.0), 4)
            tweets_data.append(
                {
                    'twitter_id': self.tw_id,
                    'tweet': tweet,
                    'impression': impression,
                    'engagement': engagement,
                    'engagement_percent': engagement_percent,
                    'target_date': self.target_month,
                    'created_at': self.today,
                }
            )

        return tweets_data

    def get_sub_data(
        self,
        page_source: str,
    ) -> dict:
        """get rt fav count."""
        engagement_percents = page_source\
            .cssselect('div#engagements-time-series-container div.time-series-value')
        link_click_counts = page_source\
            .cssselect('div#clicks-time-series-container div.time-series-value')
        rt_counts = page_source\
            .cssselect('div#retweets-time-series-container div.time-series-value')
        fav_counts = page_source\
            .cssselect('div#favs-time-series-container div.time-series-value')
        reply_counts = page_source\
            .cssselect('div#replies-time-series-container div.time-series-value')
        # check data
        if (
            (len(engagement_percents) != 1) or
            (len(link_click_counts) != 1) or
            (len(rt_counts) != 1) or
            (len(fav_counts) != 1) or
            (len(reply_counts) != 1)
        ):
            return {}

        # get data
        engagement_percent = engagement_percents[0].text.strip()
        engagement_percent = round((float(engagement_percent.replace('%', '')) / 100.0), 4)
        link_click_count = int(link_click_counts[0].text.strip().replace(',', ''))
        rt_count = int(rt_counts[0].text.strip().replace(',', ''))
        fav_count = int(fav_counts[0].text.strip().replace(',', ''))
        reply_count = int(reply_counts[0].text.strip().replace(',', ''))
        sub_data = {
            'twitter_id': self.tw_id,
            'engagement_percent': engagement_percent,
            'link_click_count': link_click_count,
            'rt_count': rt_count,
            'fav_count': fav_count,
            'reply_count': reply_count,
            'target_date': self.target_month,
            'created_at': self.today,
        }

        return sub_data

    def get_audience_insights_data(
        self,
        page_source: str,
    ) -> list:
        """get audience insights data."""
        audience_insights_data = []

        left_column_data = page_source.cssselect('div.demographics div.vertical-bar-panel')
        for data in left_column_data:
            categories = data.cssselect('div.vertical-bar-panel-header h3')
            details = data.cssselect('div.vertical-bar-chart-legend div.vertical-bar-label')
            # check data
            if (
                (len(categories) != 1) or
                (len(details) == 0)
            ):
                continue

            # get data
            category = categories[0].text.strip()
            for detail in details:
                labels = detail.cssselect('h6')
                numbers = detail.cssselect('h4')
                if (
                    (len(labels) != 1) or
                    (len(numbers) != 1)
                ):
                    return []

                label = labels[0].text.strip()
                number = numbers[0].text.strip()
                number = round((float(number.replace('%', '').replace('< ', '')) / 100.0), 2)
                audience_insights_data.append(
                    {
                        'twitter_id': self.tw_id,
                        'category': category,
                        'label': label,
                        'percent': number,
                        'target_date': self.target_month,
                        'created_at': self.today,
                    }
                )

        right_column_data = page_source.cssselect('div.demographics div.top-n-panel')
        for data in right_column_data:
            categories = data.cssselect('div.top-n-panel-header h3')
            details = data.cssselect('div.top-n-panel-table table tbody tr')
            # check data
            if (
                (len(categories) != 1) or
                (len(details) == 0)
            ):
                continue

            # get data
            category = categories[0].text.strip()
            for detail in details:
                labels = detail.cssselect('td.top-n-panel-name span')
                numbers = detail.cssselect('td.statistic-cell span')
                if (
                    (len(labels) != 1) or
                    (len(numbers) != 1)
                ):
                    return []

                label = labels[0].text.strip()
                number = numbers[0].text.strip()
                number = round((float(number.replace('%', '').replace('< ', '')) / 100.0), 2)
                audience_insights_data.append(
                    {
                        'twitter_id': self.tw_id,
                        'category': category,
                        'label': label,
                        'percent': number,
                        'target_date': self.target_month,
                        'created_at': self.today,
                    }
                )

        return audience_insights_data

    def __del__(self):
        """del."""
        # quit driver
        self.driver.close()
        self.driver.quit()
