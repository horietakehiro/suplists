from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from .base import FunctionalTest

User = get_user_model()

class MylistsTest(FunctionalTest):
    def create_pre_authenticated_session(self, email):
        user = User.objects.create(email=email)
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        ## to set a cokkie we need to first visit the domain.
        ## 404 pages load the quickest!
        self.driver.get(self.my_live_server_url + '404_no_such_url/')
        self.driver.add_cookie(
            dict(name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
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
        