import time
import random
import undetected_chromedriver as uc
import duckdb
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium import webdriver




url_template = 'https://www.tripadvisor.com/Hotels-g187791-oa{}-Rome_Lazio-Hotels.html'


class SearchIterator:
    def __init__(self):
        self.driver = None
        self.connection = None
        self.cursor = None
        self.page_number = -1
        self.url = url_template.format(self.page_number)
        self.continue_flag = True

        print('istantiated')
        self._get_driver()
        print('got driver')
        self._get_cursor()
        print('got cursor')

        # parametri vari per la ricerca
        return


    # def _get_driver(self):
    #     """ Initiate selenium (uc) driver """
    #     user_data_dir = './browser/user_data_uc' # local data folder
    #     self.driver = uc.Chrome(headless=False, user_data_dir=user_data_dir)
    #     return 
    
    def _get_driver(self):
        """ Return a driver to use selenium """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--user-data-dir=./browser/user_data')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
        self.driver = webdriver.Chrome(options=chrome_options)
        return
    
    def _get_cursor(self):
        """ Get cursor to db """
        self.connection = duckdb.connect('hotels.db')
        self.cursor = self.connection.cursor()
        return
    
    def _increase_page(self):
        """ Increase page number """
        self.page_number += 1
        self.url = url_template.format(self.page_number)
        return
    
    def _get_page(self):
        """ Get search page """
        self.driver.get(self.url)
        time.sleep(random.uniform(10, 20))
        return
    
    def _click_seeall_button(self):
        """ Click on 'See all' button """
        wait = WebDriverWait(self.driver, 50)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'See all')]"))).click()
        return
    
    def _insert_result(self, id, url):
        """ Insert result in db. If already in db, change continue flag """
        if self.cursor.execute(f'select count(*)=0 from RESULT where id={id}'):
            self.cursor.execute(f'insert into RESULT (id, url) values ({id}, \'{url}\')')
        else:
            self.continue_flag = False
        return

    def _result_card_iterator(self):
        """ Cycle through results in search page """
        for element in self.driver.find_elements('class name', 'listItem'):
            url = element.find_element('class name', 'BMQDV._F.Gv.wSSLS.SwZTJ.FGwzt.ukgoS').get_attribute('href')
            id = hash(url)
            print(url, '\n', id)
            self._insert_result(id, url)
            time.sleep(0.1)
        return
    
    def _page_iterator(self):
        """ Cycle through search pages """

        # qui la condizione deve essere qualcosa tipo un flag che è sempre true 
        # ma diventa false se tutti i risultati sono già nel db
        while self.continue_flag:
            self._increase_page()
            self._get_page()
            self._click_seeall_button()
            self._result_card_iterator()
            break
        return
    
    def run(self):
        """ Run the search iterator """
        try:
            self._page_iterator()
        finally:
            self.driver.quit()
            self.connection.close()
        return





si = SearchIterator()
si.run()



