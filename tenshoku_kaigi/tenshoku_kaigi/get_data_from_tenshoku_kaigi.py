#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://jobtalk.jp/ ."""

from datetime import datetime
import lxml.html
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep

class GetDataFromTenshokuKaigi(object):
    """get data from https://jobtalk.jp/ ."""

    def __init__(
        self,
        login_id: str,
        login_pw: str,
        company_id: str,
    ):
        """init."""
        self.company_id = company_id
        self.today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        self.good_point_text = '【良い点】'
        self.bad_point_text_1 = '【気になること・改善したほうがいい点】'
        self.bad_point_text_2 = '【気になること・改善した方がいい点】'
        self.post_date_text = 'クチコミ投稿日：'
        self.impressed_question_1 = '【印象に残った質問1】'
        self.impressed_question_2 = '【印象に残った質問2】'

        # set url
        login_url = 'https://account.jobtalk.jp/sign_in'

        # UA
        des_cap = dict(DesiredCapabilities.PHANTOMJS)
        des_cap['phantomjs.page.settings.userAgent'] = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
        )

        # set driver
        self.driver = webdriver.PhantomJS(desired_capabilities=des_cap)

        # login
        self.driver.get(login_url)
        login_id_form = self.driver\
            .find_element_by_css_selector('dd.input-parts input[name="email"]')
        login_pw_form = self.driver\
            .find_element_by_css_selector('dd.input-parts input[name="password"]')
        login_id_form.send_keys(login_id)
        login_pw_form.send_keys(login_pw)
        self.driver.find_element_by_css_selector('button.submit-button').click()
        sleep(5)

    def __get_data(
        self,
        url_fmt: str,
    ) -> list:
        """get data."""
        # param for checking next page
        next_page_flg = 1
        current_page = 1
        ret = []
        # page loop
        while next_page_flg == 1:
            url = url_fmt + str(current_page)
            self.driver.get(url)
            page_source = lxml.html.fromstring(self.driver.page_source)
            # answers
            answers = page_source.cssselect('div.c-answer-section')
            for answer in answers:
                comments = answer.cssselect('div.answer-review-text')
                review_ids = answer.cssselect('span.answer-review-id a')
                post_dates = answer.cssselect('span.answer-review-post-date')
                raitings = answer.cssselect('div.emotional-rating')
                # check data
                if (
                    (len(comments) != 1) or
                    (len(review_ids) != 1) or
                    (len(post_dates) != 1) or
                    (len(raitings) != 1)
                ):
                    continue
                # get data
                comment = comments[0]\
                    .text_content()\
                    .replace('\n', '')\
                    .replace('\r', '')\
                    .replace(self.good_point_text, '')\
                    .replace(self.bad_point_text_1, '')\
                    .replace(self.bad_point_text_2, '')\
                    .replace(self.impressed_question_1, '')\
                    .replace(self.impressed_question_2, '')\
                    .strip()
                review_id = review_ids[0].text.strip()
                post_date = post_dates[0].text.replace(self.post_date_text, '').strip()
                post_date = datetime.strptime(post_date, '%Y年%m月%d日').strftime('%Y-%m-%d')
                raiting_classes = raitings[0].classes
                raiting = ''
                for raiting_class in raiting_classes:
                    s = re.search('^rating-(\d+)$', raiting_class)
                    if s:
                        raiting = s.group(1)
                        break
                # set list
                ret.append(
                    {
                        'comment': comment,
                        'raiting': raiting,
                        'review_id': review_id,
                        'post_date': post_date,
                        'created_at': self.today,
                    }
                )

            # check next page
            next_pages = page_source.cssselect('span.pagination-item a')
            if len(next_pages) == 0:
                # not exists
                next_page_flg = 0
            else:
                next_page = next_pages[0].text.strip()
                if int(next_page) > int(current_page):
                    # exists
                    current_page = int(next_page)
                else:
                    # not exists
                    next_page_flg = 0

        return ret

    def get_reputations_data(self) -> list:
        """get reputations data."""
        reputations_url_fmt \
            = 'https://jobtalk.jp/company/%s/reputations?page=' % (self.company_id)

        return self.__get_data(reputations_url_fmt)

    def get_salaries_data(self) -> list:
        """get salaries data."""
        salaries_url_fmt = 'https://jobtalk.jp/company/%s/salaries?page=' % (self.company_id)

        return self.__get_data(salaries_url_fmt)

    def get_exams_data(self) -> list:
        """get exams data."""
        exams_url_fmt = 'https://jobtalk.jp/company/%s/exams?page=' % (self.company_id)

        return self.__get_data(exams_url_fmt)

    def __del__(self):
        """del."""
        # quit driver
        self.driver.close()
        self.driver.quit()
