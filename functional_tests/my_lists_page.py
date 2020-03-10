

class MyListsPage(object):

    def __init__(self, test):
        self.test = test

    def go_to_my_lists_page(self):
        self.test.driver.get(self.test.my_live_server_url)
        self.test.driver.find_element_by_link_text('My lists').click()
        self.test.wait_for(lambda : self.test.assertEqual(
            self.test.driver.find_element_by_tag_name('h1').text,
            'My lists'
        ))
        return self

    
