import logging
import time
import random
import undetected_chromedriver as uc
import sqlite3
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium import webdriver

url_template = 'https://www.tripadvisor.com/Hotels-g187791-oa{}-Rome_Lazio-Hotels.html'
logging.basicConfig(filename='logs/page_iterator.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 


class SearchIterator:
    def __init__(self):
        logging.info('Object instantiated')
        self.driver = None
        self.connection = None
        self.cursor = None
        self.page_number = -1
        self.url = url_template.format(self.page_number)
        self.continue_flag = False
        self.new_result_flag = True
        self.result_element = None
        self.result_id = None
        self.result_url = None
        self.result_rating = None
        self.result_reviews = None
        
        self._get_driver()
        self._get_cursor()
        
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
        logging.info('Got driver')
        return
    
    def _get_cursor(self):
        """ Get cursor to db """
        self.connection = sqlite3.connect('hotel.db')
        self.cursor = self.connection.cursor()
        logging.info('Got cursor')
        return
    
    def _increase_page(self):
        """ Increase page number """
        self.page_number += 1
        self.url = url_template.format(self.page_number*30)
        logging.info(f'Page increased: {self.url}')
        time.sleep(0.5)
        return
    
    def _get_page(self):
        """ Get search page """
        self.driver.get(self.url)
        logging.info('Got page')
        time.sleep(random.uniform(20, 40))
        return
    
    def _click_seeall_button(self):
        """ Click on 'See all' button """
        wait = WebDriverWait(self.driver, 50)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'See all')]"))).click()
        logging.info('Clicked See all button')
        time.sleep(random.uniform(20, 40))
        return
    
    def _check_continue(self):
        """ 
        Set continue_flag to True if there are new results. 
        At least one new result in the page = continue page iteration. No new results in page = stop page iteration 
        """
        if self.new_result_flag == True:
            if self.continue_flag == False:
                self.continue_flag = True
                logging.info('Set continue_flag to True')
        return
    
    def _insert_result(self):
        """ Insert result in db, only if continue_flag is True """
        if self.new_result_flag == True:
            self.cursor.execute(f'insert into RESULT (id, rating, reviews, url) values ({self.result_id}, {self.result_rating}, {self.result_reviews}, \'{self.result_url}\')')
            self.connection.commit()
            logging.info('Inserted result')
        return
    
    def _check_result(self):
        """ Check if result is already in db, change new_result_flag if so """
        if self.cursor.execute(f'select count(*)>0 from RESULT where id={self.result_id}').fetchone()[0]: # id already in db
            self.new_result_flag = False
            logging.info('Set new_result_flag to False')
        else:
            self.new_result_flag = True
            logging.info('Set new_result_flag to True')
        return
    
    def _scrape_result(self):
        """ Scrape result element """
        self.result_url = self.result_element.find_element('class name', 'BMQDV._F.Gv.wSSLS.SwZTJ.FGwzt.ukgoS').get_attribute('href')
        self.result_rating = self.result_element.find_element('class name', 'luFhX.o.W.f.u.w.JSdbl').get_attribute('aria-label').split(' ')[0]
        self.result_reviews = self.result_element.find_element('class name', 'luFhX.o.W.f.u.w.JSdbl').get_attribute('aria-label').split(' ')[-2].replace(',', '')
        self.result_id = abs(hash(self.result_url)) # sufficient collision resistance for this use case
        logging.info(f'Scraped result')
        logging.info(f'Id: {self.result_id}')
        logging.info(f'URL: {self.result_url}')
        logging.info(f'Rating: {self.result_rating}')
        logging.info(f'Reviews: {self.result_reviews}')
        return

    def _iterate_result(self):
        """ Cycle through results in search page """
        for element in self.driver.find_elements('class name', 'listItem'):
            self.result_element = element
            self._scrape_result()
            self._check_result()
            self._insert_result()
            self._check_continue()
        logging.info('Iterated all results')
        return
    
    def _reset_continue_flag(self):
        """ Reset continue_flag to False, before advancing to next page """
        self.continue_flag = False
        logging.info('Reset continue_flag to False')
        return
    
    def _load_page(self):
        """ Get page and click on 'See all' button. Retries implemented """
        i = 0
        while i < 15:
            try:
                self._get_page()
                self._click_seeall_button()
                logging.info('Loaded page')
                break
            except Exception as e:
                i += 1
                logging.error(e)
                logging.error(f'Page not loaded: error getting page or clicking button, retry {i}')
                time.sleep(15)
                continue
        return
    
    def _iterate_page(self):
        """ Cycle through search pages. Break if continue_flag is False """
        while True:
            self._increase_page()
            self._load_page()
            self._iterate_result()
            if self.continue_flag == False:
                logging.info('continue_flag is False, breaking scraping loop')
                break
            self._reset_continue_flag()
            logging.info('Done page, continuing to next page')
        return
    
    def run(self):
        """ Run the search iterator """
        try:
            self._iterate_page()
        finally:
            time.sleep(1200)
            self.driver.quit()
            self.connection.close()
        return





si = SearchIterator()
si.run()



