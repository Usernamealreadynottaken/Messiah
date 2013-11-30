from django.test import LiveServerTestCase
from selenium import webdriver


class Tests2(LiveServerTestCase):
    fixtures = ['data.json']
    server = 'http://127.0.0.1:8000/'

    def setUp(self):
        # Chrome jest wykomentowany bo nie udalo mi sie zrobic zeby dzialal, ale zostawiam
        # zeby kod nie zniknal.

        # options = webdriver.ChromeOptions()
        # options.binary_location = 'C:\Program Files (x86)\Google\Chrome\Application'

        # Bedziemy testowac na firefoxie.
        self.browser = webdriver.Firefox()

        # self.browser = webdriver.Chrome(desired_capabilities=options.to_capabilities())
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self.browser.close()
        self.browser.quit()

    #TODO: enable test
    def _test_booking_page_load(self):
        browser = self.browser
        browser.get(self.server + 'rezerwacje/')
        body = browser.find_element_by_tag_name('body')
        self.assertIn('Booking', body.text)