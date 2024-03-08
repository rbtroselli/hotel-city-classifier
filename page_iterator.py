import time
import random
import undetected_chromedriver as uc
import duckdb
import sqlite3
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium import webdriver

url_template = 'https://www.tripadvisor.com/Hotels-g187791-oa{}-Rome_Lazio-Hotels.html'
# to do:
# logging in place of prints

class SearchIterator:
    def __init__(self):
        self.driver = None
        self.connection = None
        self.cursor = None
        self.page_number = -1
        self.url = url_template.format(self.page_number)
        self.continue_flag = True
        self.result_element = None
        self.result_id = None
        self.result_url = None

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
        self.connection = sqlite3.connect('hotel.db')
        self.cursor = self.connection.cursor()
        return
    
    def _increase_page(self):
        """ Increase page number """
        self.page_number += 1
        self.url = url_template.format(self.page_number*30)
        print(self.url)
        time.sleep(5)
        return
    
    def _get_page(self):
        """ Get search page """
        self.driver.get(self.url)
        time.sleep(random.uniform(20, 30))
        return
    
    def _click_seeall_button(self):
        """ Click on 'See all' button """
        wait = WebDriverWait(self.driver, 50)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'See all')]"))).click()
        print('See all button clicked')
        return
    
    def _insert_result(self):
        """ Insert result in db, only if continue_flag is True """
        if self.continue_flag:
            self.cursor.execute(f'insert into RESULT (id, url) values ({self.result_id}, \'{self.result_url}\')')
            print('result inserted')
        return
    
    def _check_result(self):
        """ Check if result is already in db, change continue_flag if so """
        if self.cursor.execute(f'select count(*)>0 from RESULT where id={self.result_id}').fetchone()[0]:
            self.continue_flag = False
            print('continue_flag set to False')
        return
    
    def _scrape_result(self):
        """ Scrape result element """
        self.result_url = self.result_element.find_element('class name', 'BMQDV._F.Gv.wSSLS.SwZTJ.FGwzt.ukgoS').get_attribute('href')
        self.result_id = abs(hash(self.result_url)) # sufficient collision resistance for this use case
        print(self.result_url, '\n', self.result_id)
        return

    def _iterate_result(self):
        """ Cycle through results in search page. Break if continue_flag is False """
        for element in self.driver.find_elements('class name', 'listItem'):
            self.result_element = element
            self._scrape_result()
            self._check_result()
            self._insert_result()
            time.sleep(0.05)
        return
    
    def _iterate_page(self):
        """ Cycle through search pages """
        while True:
            self._increase_page()
            self._get_page()
            self._click_seeall_button()
            self._iterate_result()
            if self.continue_flag == False:
                print('continue_flag is False, breaking')
                break
        return
    
    def run(self):
        """ Run the search iterator """
        try:
            self._iterate_page()
        finally:
            self.driver.quit()
            self.connection.close()
        return





si = SearchIterator()
si.run()



