from django.conf import settings
from .base import FunctionalTest
from .server_tools import create_session_on_server
from .management.commands.create_session import create_preauthenticated_session

import sys

class MylistsTest(FunctionalTest):


    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        email = 'edith@example.com'
        self.driver.get(self.my_live_server_url)
        self.wait_to_be_logged_out(email=email)

        # Edith is a logged-in user
        self.create_pre_authenticated_session(email=email)
        self.driver.get(self.my_live_server_url)
        self.wait_to_be_logged_in(email=email)
        

    def test_logged_in_users_lists_are_saevd_as_my_lists(self):
        #Edith is a logged-in user
        self.create_pre_authenticated_session('edith@example.com')
        
        # She goes to the home page and starts a list
        self.driver.get(self.my_live_server_url)
        self.add_list_item('Reticulate splines')
        self.add_list_item('Immanentize eschaton')
        first_list_url = self.driver.current_url

        #she notices a "My lists" lnik, for the first time
        self.driver.find_element_by_link_text('My lists').click()

        # She sees that her list is in there, named according to its
        # first list item
        self.wait_for(
            lambda : self.driver.find_element_by_link_text('Reticulate splines')
        )
        self.driver.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(
            lambda : self.assertEqual(self.driver.current_url, first_list_url)
        )

        # she decides to start another list, just to see
        self.driver.get(self.my_live_server_url)
        self.add_list_item('Click cows')
        second_url = self.driver.current_url

        # Under "my lsits", her new list appears
        self.driver.find_element_by_link_text('My lists').click()
        self.wait_for(
            lambda : self.driver.find_element_by_link_text('Click cows')
        )
        self.driver.find_element_by_link_text('Click cows').click()
        self.wait_for(
            lambda : self.assertEqual(self.driver.current_url, second_url)
        )

        #she logged out. The "my lists" option disappears
        self.driver.find_element_by_link_text('Log out').click()
        self.wait_for(lambda : self.assertEqual(
            self.driver.find_elements_by_link_text('My lists'), []
            )
        )