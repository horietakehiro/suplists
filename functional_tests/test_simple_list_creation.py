from .base import FunctionalTest

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


MAX_WAIT=10


class NewVisitorTest(FunctionalTest):


    def test_can_start_a_list_for_one_user(self):
        # get the home page of new to-do app.
        # self.driver.get('http://localhost:9090')
        self.driver.get(self.my_live_server_url)


        # this page's title and heade mention the 'to-do' lists
        assert 'To-Do' in self.driver.title
        self.assertIn('To-Do', self.driver.title)
        header_text = self.driver.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # she is invited to enter to-do item straight away
        inputbox = self.driver.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # she types "Byy peacock's feather" into a text box
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        # when she hists the enter, the page updates and now the page lists
        # "1: Buy peacock's feather "
        time.sleep(1)
        self.wait_for_row_in_list_rable('1: Buy peacock feathers')

        # There is still a text box that inviting her to add another item.
        # she enters "Use peacock feathers to make a fly"
        inputbox = self.driver.find_element_by_id('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # THe page updates again, and now shows both items on her list
        self.wait_for_row_in_list_rable('1: Buy peacock feathers')
        self.wait_for_row_in_list_rable('2: Use peacock feathers to make a fly')


    def test_multiple_users_can_starat_lists_at_different_urls(self):
        # she starts a new to-do list
        self.driver.get(self.my_live_server_url)
        inputbox = self.driver.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_list_rable('1: Buy peacock feathers')
        edith_list_url = self.driver.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        #
        # now a new user, Francis comes along to the site
        #

        # we use a new browser session to make sure that
        # no inofrmation of edith is coming from cookie etc
        self.driver.quit() 
        self.driver  = webdriver.Remote(
            command_executor=f'http://{addr}/wd/hub',
            options=option,
        )


        # Francis visits the home page.
        # THere is no sign of Edith's lsit
        self.driver.get(self.my_live_server_url)
        page_text = self.driver.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # Francis starts a new lists by entering a new item.
        # He is less interesting than Edith
        inputbox = self.driver.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_list_rable('1: Buy milk')

        # Francis gets his own unique url
        francis_list_url = self.driver.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Again, there is no trace of Edith's list
        page_text = self.driver.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)

        # satisfied, the both go back to sleep
