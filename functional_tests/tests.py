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


# class NewVisitorTest(LiveServerTestCase):
class NewVisitorTest(StaticLiveServerTestCase):

    # define live_server_url by myself beause 
    # selenium server is running outside the container , and
    # port forward mapping cannot be changed dynamically
    port = 8080
    host = '0.0.0.0'

    # Don't change original "live_server_url" atttribute
    my_live_server_url = 'http://localhost:9090/'

    # server_thread_class = MyThreat
    def setUp(self):
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.my_live_server_url = 'http://' + staging_server
        
        self.driver = webdriver.Remote(
            command_executor=f'http://{addr}/wd/hub',
            options=option,
        )

    def tearDown(self):
        self.driver.quit()

    def wait_for_row_in_list_rable(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.driver.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')      
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

                          

    def check_for_row_in_list_table(self, row_text):
        table = self.driver.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])


    def test_can_start_a_list_and_retrieve_it_later(self):
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
        self.wait_for_row_in_list_rable('1: Buy peacock feathers')

        # There is still a text box that inviting her to add another item.
        # she enters "Use peacock feathers to make a fly"
        inputbox = self.driver.find_element_by_id('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)

        # THe page updates again, and now shows both items on her list
        self.wait_for_row_in_list_rable('1: Buy peacock feathers')
        self.wait_for_row_in_list_rable('2: Use peacock feathers to make a fly')


        # self.fail('Finish the test !')

        

        # she wonders whether the site will remember her list.
        # Then she sees that the site has generated a uniwue URL for her -- 
        # there is some explanatory test to that effect.

        # she visits that URL - her to-do lists is still there.

     
        # satisfied, she gers bacj to slep

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


        # self.fail('Finish the test !')

        

        # she wonders whether the site will remember her list.
        # Then she sees that the site has generated a uniwue URL for her -- 
        # there is some explanatory test to that effect.

        # she visits that URL - her to-do lists is still there.

     
        # satisfied, she gers bacj to slep

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


    def test_layout_and_styling(self):
        # Edith goes to the home page
        self.driver.get(self.my_live_server_url)
        self.driver.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        inputbox = self.driver.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10,
        )


        # she starts a new list and sees the input is nicely
        # created there too
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_rable('1: testing')
        inputbox = self.driver.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10,
        )

    @skip
    def test_cannnot_add_empty_list_items(self):
        # Edith goes the home page and accidentlly tries to submit 
        # an empty list item. She hits Enter on the empty input box

        # The home page refreshes, and there is an erro message saying
        # that list items cannot be blank

        # She tries agein with some text for the item, which now works

        # Perversely, she now decides to submit a second blank lists item

        # SHe receives a similar warning on the list page

        # And she can correct it by filling some text in 

        self.fail('white me!')