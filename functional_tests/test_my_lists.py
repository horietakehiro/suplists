from django.conf import settings
from .base import FunctionalTest
from .server_tools import create_session_on_server
from .management.commands.create_session import create_preauthenticated_session

import sys

class MylistsTest(FunctionalTest):
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

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        email = 'edith@example.com'
        self.driver.get(self.my_live_server_url)
        self.wait_to_be_logged_out(email=email)

        # Edith is a logged-in user
        self.create_pre_authenticated_session(email=email)
        self.driver.get(self.my_live_server_url)
        self.wait_to_be_logged_in(email=email)
        