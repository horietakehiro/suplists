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

from .server_tools import reset_database

MAX_WAIT=10

def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
    return modified_fn

# class NewVisitorTest(LiveServerTestCase):
class FunctionalTest(StaticLiveServerTestCase):

    # define live_server_url by myself beause 
    # selenium server is running outside the container , and
    # port forward mapping cannot be changed dynamically
    port = 8080
    host = '0.0.0.0'

    # Don't change original "live_server_url" atttribute
    my_live_server_url = 'http://localhost:9090/'

    driver = None

    def setUp(self):
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.my_live_server_url = 'http://' + self.staging_server + '/'

            reset_database(self.staging_server)
        
        if self.driver is None:
            self.driver = webdriver.Remote(
                command_executor=f'http://{addr}/wd/hub',
                options=option,
            )

    def tearDown(self):
        self.driver.quit()
        self.driver = None


    @wait
    def wait_for_row_in_list_rable(self, row_text):
        table = self.driver.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')      
        self.assertIn(row_text, [row.text for row in rows])


    @wait
    def wait_for(self, fn):
        return fn()
                
    def get_item_input_box(self):
        return self.driver.find_element_by_id('id_text')
        
    @wait
    def wait_to_be_logged_in(self, email):
        self.driver.find_element_by_link_text('Log out')
        navbar = self.driver.find_element_by_css_selector('.navbar')
        self.assertIn(email, navbar.text)

    @wait
    def wait_to_be_logged_out(self, email):
        self.driver.find_element_by_name('email')
        navbar = self.driver.find_element_by_css_selector('.navbar')
        self.assertNotIn(email, navbar.text)
        