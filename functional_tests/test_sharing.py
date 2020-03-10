from selenium import webdriver
from .base import FunctionalTest
import os
from .list_page import ListPage
from .my_lists_page import MyListsPage

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
        list_page = ListPage(self).add_list_item('Get help')

        # She notices that a "Share this list" option
        share_box = list_page.get_share_box()
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'yout-friend@example.com',
        )

        # She shares her list.
        #  The page updates to say that it's shared with Oniferous:
        list_page.share_list_with('oniciferous@example.com')


        #Oniciferous now goes to the lists page with his driver
        self.driver = oni_driver
        MyListsPage(self).go_to_my_lists_page()

        # he sees Edith's list in there!
        self.driver.find_element_by_link_text('Get help').click()

        #On the list page, Oniciferous can see says that it's Edith's list
        self.wait_for(lambda : self.assertEqual(
            list_page.get_list_owner(),
            'edith@example.com'
        ))
        #He adds an item to the list
        list_page.add_list_item('Hi Edith!')

        #When Edith refreshes the page, she sees Oniciferous's addition
        self.driver = edith_driver
        self.driver.refresh()
        list_page.wait_for_row_in_list_table('Hi Edith!', 2)
        