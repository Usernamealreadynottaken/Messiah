from django.test import LiveServerTestCase
from selenium import webdriver
from django.core.urlresolvers import reverse

# Modele
from Hotel.models import Usluga


class SomeAdminTest(LiveServerTestCase):
    fixtures = ['data.json']

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.binary_location = 'C:\Program Files (x86)\Google\Chrome\Application'

        self.browser = webdriver.Firefox()
        # self.browser = webdriver.Chrome(desired_capabilities=options.to_capabilities())
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.close()
        self.browser.quit()

    def test_rezerwacje_valiation(self):
        browser = self.browser
        browser.get('http://127.0.0.1:8000/rezerwacje/')
        body = browser.find_element_by_tag_name('body')
        self.assertIn('Rezerwacje', body.text)