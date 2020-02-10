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

        # The home page refreshes, and there is an erro message saying
        # that list items cannot be blank

        # She tries agein with some text for the item, which now works

        # Perversely, she now decides to submit a second blank lists item

        # SHe receives a similar warning on the list page

        # And she can correct it by filling some text in 

        self.fail('white me!')