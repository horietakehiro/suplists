from selenium import webdriver
from .base import FunctionalTest
import os
addr = os.environ.get('SSA')
option = webdriver.FirefoxOptions()

def quit_if_possible(driver):
    try:
        driver.quit()
    except:
        pass

class SharingTest(FunctionalTest):

    def test_can_share_a_list_with_another_user(self):
        #Edith is a logged in user
        self.create_pre_authenticated_session('edith@example.com')
        edith_driver = self.driver
        self.addCleanup(lambda : quit_if_possible(edith_driver))

        # Her friend Oniciferous is also hanging out on the lists site
        if self.is_local:
            oni_driver = webdriver.Remote(
                command_executor=f'http://{addr}/wd/hub',
                options=option,
            )
        else:
            oni_driver = webdriver.Firefox()
        self.addCleanup(lambda : quit_if_possible(oni_driver))
        self.driver = oni_driver
        self.create_pre_authenticated_session('oniciferous@example.com')

        # Edith goes to the home page and starts a lisst
        self.driver = edith_driver
        self.driver.get(self.my_live_server_url)
        self.add_list_item('Get help')

        # She notices that a "Share this list" option
        share_box = self.driver.find_element_by_css_selector(
            'input[name="sharee"]'
        )
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'yout-friend@example.com',
        )
        