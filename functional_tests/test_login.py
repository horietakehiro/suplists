from django.core import mail
from selenium.webdriver.common.keys import Keys
import re

from .base import FunctionalTest

TEST_EMAIL='edith@example.com'
SUBJECT='Your login link for Superlists'

class LoginTest(FunctionalTest):
    def test_can_get_email_link_to_log_in(self):
        # Edith goes to the awsome superlists stie
        # and notices a "Log in" section in the navbar for the first time
        # It's telling her to enter her email address, so she does
        self.driver.get(self.my_live_server_url)
        self.driver.find_element_by_name('email').send_keys(TEST_EMAIL)
        self.driver.find_element_by_name('email').send_keys(Keys.ENTER)

        # A message appears telling her an email has been sent
        self.wait_for(lambda : self.assertIn(
            'Check your email',
            self.driver.find_element_by_tag_name('body').text
        ))

        #She checks her email and finds a message
        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(email.subject, SUBJECT)

        # It has a url link in it
        self.assertIn('Use this link to log in', email.body)
        url_search = re.search(r'http://.+$', email.body)
        if not url_search:
            self.fail(f'Could not find url in email body\n{email.body}')
        url = url_search.group(0)
        self.assertIn(self.my_live_server_url, url)

        # She clicks it
        self.driver.get(url)

        # she is logged in
        self.wait_for(
            lambda : self.driver.find_element_by_link_text('Log out')
        )
        navbar = self.driver.find_element_by_css_selector('.navbar')
        self.assertIn(TEST_EMAIL, navbar.text)
        