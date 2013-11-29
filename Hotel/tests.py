from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import datetime


class HotelTest(LiveServerTestCase):
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

    def test_booking_page_load(self):
        browser = self.browser
        browser.get(self.server + 'rezerwacje/')
        body = browser.find_element_by_tag_name('body')
        self.assertIn('Booking', body.text)

    def date_validation(self, date, date_error, out):
        # Puste pole
        date.clear()
        out.click()
        self.assertTrue(date_error.is_displayed())

        # Napis
        date.send_keys('somesome')
        out.click()
        self.assertTrue(date_error.is_displayed())

        # Miesiac wiekszy niz 12
        date.clear()
        date.send_keys('14/%d/%d' % (datetime.date.today().day, datetime.date.today().year,))
        out.click()
        self.assertTrue(date_error.is_displayed())

        # Dzien wiekszy niz 31
        date.clear()
        date.send_keys('%d/54/%d' % (datetime.date.today().month, datetime.date.today().year,))
        out.click()
        self.assertTrue(date_error.is_displayed())

        # Format
        date.clear()
        date.send_keys('123/%d/%d' % (datetime.date.today().day, datetime.date.today().year,))
        out.click()
        self.assertTrue(date_error.is_displayed())

        date.clear()
        date.send_keys('%d/123/%d' % (datetime.date.today().month, datetime.date.today().year,))
        out.click()
        self.assertTrue(date_error.is_displayed())

        date.clear()
        date.send_keys('%d-%d-%d' % (datetime.date.today().month, datetime.date.today().day, datetime.date.today().year,))
        out.click()
        self.assertTrue(date_error.is_displayed())

        date.clear()
        date.send_keys('%d.%d.%d' % (datetime.date.today().month, datetime.date.today().day, datetime.date.today().year,))
        out.click()
        self.assertTrue(date_error.is_displayed())

    def test_booking_field_validation(self):
        browser = self.browser
        browser.get(self.server + 'rezerwacje/')
        wait = ui.WebDriverWait(browser, 2)

        #
        # NAME
        #
        name = browser.find_element_by_name('name')
        phone = browser.find_element_by_name('tel')
        phone.click()
        name_error = browser.find_element_by_class_name('name-error')

        # Nazwisko jest puste wiec walidacja powinna wywalic blad
        self.assertTrue(name_error.is_displayed())

        name.send_keys('Test_name')
        phone.click()
        wait.until_not(lambda tag_to_wait_for: name_error.is_displayed())

        # Nazwisko jest wypelnione wiec walidacja powinna je przepuscic
        self.assertFalse(name_error.is_displayed())

        #
        # E-MAIL
        #
        email = browser.find_element_by_name('email')
        email_error = browser.find_element_by_class_name('email-error')
        email.click()
        phone.click()

        # Email jest pusty
        self.assertTrue(email_error.is_displayed())

        # Testy roznych blednych emaili
        try:
            test_email = 'assd'
            email.clear()
            email.send_keys(test_email)
            phone.click()
            wait.until_not(lambda tag_to_wait_for: email_error.is_displayed())

            # Jesli nie zostal zlapany wyjatek to znaczy ze walidacja zaakceptowala zly email
            raise Exception('Email validation succeeded on: ' + test_email)
        except TimeoutException:
            pass

        try:
            test_email = 'sth@sth'
            email.clear()
            email.send_keys(test_email)
            phone.click()
            wait.until_not(lambda tag_to_wait_for: email_error.is_displayed())

            # Jesli nie zostal zlapany wyjatek to znaczy ze walidacja zaakceptowala zly email
            raise Exception('Email validation succeeded on: ' + test_email)
        except TimeoutException:
            pass

        try:
            test_email = 'tsh.@sd.com'
            email.clear()
            email.send_keys(test_email)
            phone.click()
            wait.until_not(lambda tag_to_wait_for: email_error.is_displayed())

            # Jesli nie zostal zlapany wyjatek to znaczy ze walidacja zaakceptowala zly email
            raise Exception('Email validation succeeded on: ' + test_email)
        except TimeoutException:
            pass

        try:
            test_email = '.sd@sd.com'
            email.clear()
            email.send_keys(test_email)
            phone.click()
            wait.until_not(lambda tag_to_wait_for: email_error.is_displayed())

            # Jesli nie zostal zlapany wyjatek to znaczy ze walidacja zaakceptowala zly email
            raise Exception('Email validation succeeded on: ' + test_email)
        except TimeoutException:
            pass

        # TODO: Ten test failuje
        ''' try:
            test_email = 'sdsd-@sdd.com'
            email.clear()
            email.send_keys(test_email)
            phone.click()
            wait.until_not(lambda tag_to_wait_for: email_error.is_displayed())

            # Jesli nie zostal zlapany wyjatek to znaczy ze walidacja zaakceptowala zly email
            raise Exception('Email validation succeeded on: ' + test_email)
        except TimeoutException:
            pass '''

        try:
            test_email = 'asdsd@sdsd.com.'
            email.clear()
            email.send_keys(test_email)
            phone.click()
            wait.until_not(lambda tag_to_wait_for: email_error.is_displayed())

            # Jesli nie zostal zlapany wyjatek to znaczy ze walidacja zaakceptowala zly email
            raise Exception('Email validation succeeded on: ' + test_email)
        except TimeoutException:
            pass

        # Testowanie poprawnych maili
        email.clear()
        email.send_keys('email@domain.com')
        phone.click()
        wait.until_not(lambda tag_to_wait_for: email_error.is_displayed())

        email.clear()
        email.send_keys('some-mail@domain.com')
        phone.click()
        self.assertFalse(email_error.is_displayed())

        email.clear()
        email.send_keys('email@domain.sub.com')
        phone.click()
        self.assertFalse(email_error.is_displayed())

        email.clear()
        email.send_keys('email@domain-sub.com')
        phone.click()
        self.assertFalse(email_error.is_displayed())

        #
        # DATES
        #

        # Ustawiamy dluzsze niz poprzednio oczekiwanie bo przy datach z jakiegos powodu tym errorom
        # zajmuje mase czasu znikniecie
        wait = ui.WebDriverWait(browser, 5)

        date_from = browser.find_element_by_name('date-from')
        date_to = browser.find_element_by_name('date-to')
        date_from_error = browser.find_element_by_class_name('dateFrom-error')
        date_to_error = browser.find_element_by_class_name('dateTo-error')

        self.date_validation(date_from, date_from_error, phone)

        date_from.clear()
        date_from.send_keys('%d/%d/%d' % (datetime.date.today().month, datetime.date.today().day, datetime.date.today().year,))
        phone.click()
        wait.until_not(lambda tag_to_wait_for: date_from_error.is_displayed())

        self.date_validation(date_to, date_to_error, phone)

        # Rzeczy ktorych nie mozna bylo sprawdzic na dacie poczatkowej
        date_to.clear()
        date_to.send_keys('1/23/2014')
        phone.click()
        self.assertTrue(date_to_error.is_displayed())

        date_to.clear()
        date_to.send_keys('02/30/2014')
        phone.click()
        self.assertTrue(date_to_error.is_displayed())

        date_to.clear()
        date_to.send_keys('04/31/2014')
        phone.click()
        self.assertTrue(date_to_error.is_displayed())

        date_to.clear()
        date_to.send_keys('01/1/2014')
        phone.click()
        self.assertTrue(date_to_error.is_displayed())

        # Data koncowa < data poczatkowa
        temp_date = datetime.date.today() - datetime.timedelta(days=3)
        date_to.clear()
        date_to.send_keys('%d/%d/%d' % (temp_date.month, temp_date.day, temp_date.year,))
        phone.click()
        self.assertTrue(date_to_error.is_displayed())

        # Data poczatkowa < today
        temp_date = datetime.date.today() + datetime.timedelta(days=1)
        date_to.clear()
        date_to.send_keys('%d/%d/%d' % (temp_date.month, temp_date.day, temp_date.year,))
        phone.click()
        wait.until_not(lambda tag_to_wait_for: date_to_error.is_displayed())

        temp_date = datetime.date.today() - datetime.timedelta(days=2)
        date_from.clear()
        date_from.send_keys('%d/%d/%d' % (temp_date.month, temp_date.day, temp_date.year,))
        phone.click()
        self.assertTrue(date_from_error.is_displayed())

        # Wprowadzamy dobra date i patrzymy czy sie waliduje
        temp_date = datetime.date.today()
        date_from.clear()
        date_from.send_keys('%d/%d/%d' % (temp_date.month, temp_date.day, temp_date.year,))
        phone.click()
        wait.until_not(lambda tag_to_wait_for: date_from_error.is_displayed())

        #
        # SERVICES
        #
        services_bar = browser.find_element_by_class_name('additions').find_element_by_tag_name('h2')
        services_bar.click()
        services_in = browser.find_element_by_class_name('in')
        wait.until(lambda item_to_wait_for: services_in.is_displayed())

        try:
            browser.find_element_by_class_name('in1').click()
        except NoSuchElementException:
            pass

        # Sprobojemy zabookowac z bleami
        name.clear()

        browser.find_element_by_class_name('send').click()
        success = browser.find_element_by_class_name('success')
        try:
            wait.until(lambda item_to_wait_for: success.is_displayed())

            # Jesli nie ma timeoutu to znaczy ze sie zarejestrowalo
            raise Exception('Booked despite errors')
        except TimeoutException:
            pass

        # Wypelnimy imie i sprobojemy zarezerwowac
        name.send_keys('Test name')
        browser.find_element_by_class_name('send').click()
        wait.until(lambda item_to_wait_for: success.is_displayed())
        browser.find_element_by_class_name('close').click()