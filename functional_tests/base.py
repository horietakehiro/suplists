import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from .management.commands.create_session import create_preauthenticated_session
from .server_tools import create_session_on_server
from django.conf import settings

addr = os.environ.get('SSA')
option = webdriver.FirefoxOptions()

import time
# import unittest
# from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from unittest import skip

from .server_tools import reset_database

MAX_WAIT=10

SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps',
)

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
    # port = 8080


    # Don't change original "live_server_url" atttribute
    is_local = os.environ.get('IS_LOCAL', False)
    if is_local:
        port = 8888
        host = '0.0.0.0'
        my_live_server_url = 'http://localhost:9999/'
    else:
        my_live_server_url = None

    driver = None

    def create_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)
        else:
            session_key = create_preauthenticated_session(email)

        ## to set a cokkie we need to first visit the domain.
        ## 404 pages load the quickest!
        self.driver.get(self.my_live_server_url + '404_no_such_url/')
        self.driver.add_cookie(
            dict(name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
            )
        )
        
    def setUp(self):
        if self.my_live_server_url is None:
            self.my_live_server_url = self.live_server_url + '/'
        
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.my_live_server_url = 'http://' + self.staging_server + ':' +  str(self.port) + '/'

            reset_database(self.staging_server)
        
        if self.driver is None:
            if self.is_local:
                self.driver = webdriver.Remote(
                    command_executor=f'http://{addr}/wd/hub',
                    options=option,
                )
            else:
                self.driver = webdriver.Firefox()


    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.driver.window_handles):
                self._windowid = ix
                self.driver.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()

        self.driver.quit()
        self.driver = None
        super().tearDown()


    def _test_has_failed(self):
        # slightly obscure but counlD'nt fund a better way.
        return any(error for (method, error) in self._outcome.errors)

    def take_screenshot(self):
        filename = self._get_filename() + '.png'
        print('screenshotting to ', filename)
        self.driver.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + '.html'
        print('dumping page HTML to', filename)
        with open(filename, 'w') as f:
            f.write(self.driver.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        return '{folder}/{classname}.{method}-window{window}-{timestamp}'.format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            window=self._windowid,
            timestamp=timestamp,
        )
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
        

    def add_list_item(self, item_text):
        num_rows = len(self.driver.find_elements_by_css_selector('#id_list_table tr'))
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_rable(f'{item_number}: {item_text}')
