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


        # The browser intercepts the request, and does not load the list page
        self.wait_for(lambda : self.driver.find_element_by_css_selector(
            '#id_text:invalid'
        ))


        # She tries agein with some text for the item, which now works
        self.get_item_input_box().send_keys('Buy milk')
        self.wait_for(lambda : self.driver.find_element_by_css_selector(
            '#id_text:valid'
        ))

        # And she can submit it successfully 
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_rable('1: Buy milk')

        # Perversely, she now decides to submit a second blank lists item
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Again, the browser will not comply
        self.wait_for(lambda : self.driver.find_element_by_css_selector(
            '#id_text:invalid'
        ))

        # And she can correct it by filling some text in 
        self.get_item_input_box().send_keys('Make tea')
        self.wait_for(lambda : self.driver.find_element_by_css_selector(
            '#id_text:valid'
        ))
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_rable('1: Buy milk')
        self.wait_for_row_in_list_rable('2: Make tea')


        # self.fail('finish the test!')