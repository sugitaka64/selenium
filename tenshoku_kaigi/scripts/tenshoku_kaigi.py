#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://jobtalk.jp/ ."""

from datetime import datetime
import lxml.html
import re
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
from time import sleep

if __name__ == '__main__':
    print('%s %s start.' % (datetime.today(), __file__))

    # config
    login_url = 'https://account.jobtalk.jp/sign_in'
    login_id = 'xxx'
    login_pw = 'yyy'
    company_id = '22191'
    reputations_url_fmt = 'https://jobtalk.jp/company/%s/reputations?page=' % (company_id)
    salaries_url_fmt = 'https://jobtalk.jp/company/%s/salaries?page=' % (company_id)
    exams_url_fmt = 'https://jobtalk.jp/company/%s/exams?page=' % (company_id)
    good_point_text = '【良い点】'
    bad_point_text_1 = '【気になること・改善したほうがいい点】'
    bad_point_text_2 = '【気になること・改善した方がいい点】'
    post_date_text = 'クチコミ投稿日：'

    # UA
    des_cap = dict(DesiredCapabilities.PHANTOMJS)
    des_cap['phantomjs.page.settings.userAgent'] = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
    )

    # set driver
    driver = webdriver.PhantomJS(desired_capabilities=des_cap)

    # login
    driver.get(login_url)
    try:
        login_id_form = driver\
            .find_element_by_css_selector('dd.input-parts input[name="email"]')
        login_pw_form = driver\
            .find_element_by_css_selector('dd.input-parts input[name="password"]')
        login_id_form.send_keys(login_id)
        login_pw_form.send_keys(login_pw)
        driver.find_element_by_css_selector('button.submit-button').click()
        sleep(5)
    except NoSuchElementException:
        print('error.')
        sys.exit(1)

    # reputations
    # param for checking next page
    next_page_flg = 1
    current_page = 1
    tmp = []
    # page loop
    while next_page_flg == 1:
        reputations_url = reputations_url_fmt + str(current_page)
        driver.get(reputations_url)
        page_source = lxml.html.fromstring(driver.page_source)
        # answers
        answers = page_source.cssselect('div.c-answer-section')
        for answer in answers:
            comments = answer.cssselect('div.answer-review-text')
            review_ids = answer.cssselect('span.answer-review-id a')
            post_dates = answer.cssselect('span.answer-review-post-date')
            raitings = answer.cssselect('div.emotional-rating')
            # check data
            if (
                (len(comments) != 1)
                or (len(review_ids) != 1)
                or (len(post_dates) != 1)
                or (len(raitings) != 1)
            ):
                continue
            # get data
            comment = comments[0]\
                .text_content()\
                .replace('\n', '')\
                .replace('\r', '')\
                .replace(good_point_text, '')\
                .replace(bad_point_text_1, '')\
                .replace(bad_point_text_2, '')\
                .strip()
            review_id = review_ids[0].text.strip()
            post_date = post_dates[0].text.replace(post_date_text, '').strip()
            raiting_classes = raitings[0].classes
            raiting = ''
            for raiting_class in raiting_classes:
                s = re.search('^rating-(\d+)$', raiting_class)
                if s:
                    raiting = s.group(1)
                    break
            # set list
            tmp.append([comment, raiting, review_id, post_date])

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

    # make csv file
    print(tmp)

    # quit driver
    driver.close()
    driver.quit()

    print('%s %s end.' % (datetime.today(), __file__))
    sys.exit(0)
