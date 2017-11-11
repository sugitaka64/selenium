#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""get data from https://jobtalk.jp/ ."""

import os
import sys
import unittest
from unittest import mock

try:
    import get_data_from_tenshoku_kaigi
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../tenshoku_kaigi')
    import get_data_from_tenshoku_kaigi

class GetDataFromTenshokuKaigiTests(unittest.TestCase):
    """get data from https://jobtalk.jp/ ."""

    def setUp(self):
        """set up."""
        self.company_id = 'xxxxx'

        # create model
        self.gdftk = get_data_from_tenshoku_kaigi.GetDataFromTenshokuKaigi(
            'xxxxx',
            'yyyyy',
            self.company_id
        )

        # set mock
        test_html = '<html><body>test</body></html>'
        self.gdftk.driver.get = mock.Mock()
        self.gdftk.driver.get.return_value = test_html
        self.gdftk.driver.find_element_by_css_selector = mock.Mock()
        self.gdftk.driver.find_element_by_css_selector.click = mock.Mock()
        self.gdftk.driver.find_element_by_css_selector.click.return_value = True

    def test_init(self):
        """init."""
        self.assertEqual(self.gdftk.company_id, self.company_id)
        self.assertTrue(isinstance(self.gdftk.driver.page_source, str))

    def test_get_reputations_data(self):
        """get reputations data."""
        self.gdftk.__get_data = mock.Mock()
        self.gdftk.__get_data.return_value = []
        self.assertEqual(self.gdftk.get_reputations_data(), [])

    def test_get_salaries_data(self):
        """get salaries data."""
        self.gdftk.__get_data = mock.Mock()
        self.gdftk.__get_data.return_value = []
        self.assertEqual(self.gdftk.get_salaries_data(), [])

    def test_get_exams_data(self):
        """get exams data."""
        self.gdftk.__get_data = mock.Mock()
        self.gdftk.__get_data.return_value = []
        self.assertEqual(self.gdftk.get_exams_data(), [])
