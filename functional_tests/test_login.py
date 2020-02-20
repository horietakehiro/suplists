from django.core import mail
from selenium.webdriver.common.keys import Keys
import re
import os
import poplib
import time

from .base import FunctionalTest

TEST_EMAIL='edith@example.com'
SUBJECT='Your login link for Superlists'

class LoginTest(FunctionalTest):

    def wait_for_email(self, test_email, subject):
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        email_id = None
        start = time.time()
        inbox = poplib.POP3_SSL('pop.gmail.com', 995)
        try:
            inbox.user(test_email)
            inbox.pass_(os.environ.get('GMAIL_PASSWORD'))
            while time.time() - start < 60:
                # get 10 newest messages
                count, _ = inbox.stat()
                for i in reversed(range(max(1, count - 10), count + 1)):
                    print('getting msg', i)
                    _, lines, _ = inbox.retr(i)
                    lines = [l.decode('utf-8') for l in lines]
                    print(lines)
                    if f'Subject: {subject}' in lines:
                        email_id = i
                        body = '\n'.join(lines)
                        return body
                time.sleep(5)
        finally:
            if email_id:
                inbox.dele(email_id)
            inbox.quit()

    def test_can_get_email_link_to_log_in(self):
        # Edith goes to the awsome superlists stie
        # and notices a "Log in" section in the navbar for the first time
        # It's telling her to enter her email address, so she does
        if self.staging_server:
            test_email = 'superlist.test@gmail.com'
        else:
            test_email = 'edith@example.com'
        
        self.driver.get(self.my_live_server_url)
        self.driver.find_element_by_name('email').send_keys(test_email)
        self.driver.find_element_by_name('email').send_keys(Keys.ENTER)

        # A message appears telling her an email has been sent
        self.wait_for(lambda : self.assertIn(
            'Check your email',
            self.driver.find_element_by_tag_name('body').text
        ))

        #She checks her email and finds a message
        # email = mail.outbox[0]
        # self.assertIn(TEST_EMAIL, email.to)
        # self.assertEqual(email.subject, SUBJECT)
        body = self.wait_for_email(test_email, SUBJECT)

        # It has a url link in it
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body\n{body}')
        url = url_search.group(0)

        # dismiss port number
        url_splitted = self.my_live_server_url.split(':')
        tmp_url = ':'.join(url_splitted[:2])
        self.assertIn(tmp_url, url)

        # She clicks it
        if len(url_splitted) == 3:
            port = url_splitted[-1][:-1]

            head, tail = url.split('/accounts/login?token=')
            url = head + ':' + port + '/accounts/login?token=' + tail

        print(url)
        self.driver.get(url)

        # she is logged in
        self.wait_to_be_logged_in(email=test_email)
        
        # now she logs out
        self.driver.find_element_by_link_text('Log out').click()

        #She is logged out
        self.wait_to_be_logged_out(email=test_email)

