import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
addr = os.environ.get('SSA')
option = webdriver.FirefoxOptions()

import time
# import unittest
# from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from unittest import skip

from .base import FunctionalTest




MAX_WAIT=10

class ItemValidationTest(FunctionalTest):
    
    def test_cannnot_add_empty_list_items(self):
        # Edith goes the home page and accidentlly tries to submit 
        # an empty list item. She hits Enter on the empty input box
        self.driver.get(self.my_live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)


        # The home page refreshes, and there is an erro message saying
        # that list items cannot be blank
        self.wait_for(lambda: self.assertEqual(
            self.driver.find_element_by_css_selector('.has-error').text,
            "You can't have an empty list item"
        ))


        # She tries agein with some text for the item, which now works
        self.get_item_input_box().send_keys('Buy milk')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_rable('1: Buy milk')

        # Perversely, she now decides to submit a second blank lists item
        self.get_item_input_box().send_keys(Keys.ENTER)

        # SHe receives a similar warning on the list page
        self.wait_for(lambda: self.assertEqual(
            self.driver.find_element_by_css_selector('.has-error').text,
            "You can't have an empty list item"
        ))

        # And she can correct it by filling some text in 
        self.get_item_input_box().send_keys('Make tea')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_rable('1: Buy milk')
        self.wait_for_row_in_list_rable('2: Make tea')


        self.fail('finish the test!')