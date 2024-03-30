import logging
import time
import random
import sqlite3
import hashlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium import webdriver
from _config import LOG_FOLDER_PATH


class BaseIterator:
    def __init__(self, test=True, log_file_name='test.log', db_name='test.db', db_connection=True, browser_driver=True):
        if test:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # log to console
        else:
            logging.basicConfig(filename=LOG_FOLDER_PATH/log_file_name, filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  # log to file
        logging.info('Object instantiated')
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.driver = None
        self._get_cursor() if db_connection else None
        self._get_driver() if browser_driver else None
        logging.info('Initialization complete')
        return
    

    # connection functions
    
    def _get_cursor(self):
        """ Get cursor to db """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            logging.info('Got cursor')
        except Exception as e:
            logging.error('Error getting cursor')
            logging.exception('An error occurred')
        return
    
    def _get_driver(self):
        """ Return a driver to use selenium """
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--user-data-dir=./browser/user_data')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled') 
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) # remove "Chrome is being controlled by an automated software"
            chrome_options.add_experimental_option("useAutomationExtension", False) 
            # chrome_options.add_argument('Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_8 like Mac OS X) AppleWebKit/534.2 (KHTML, like Gecko) FxiOS/17.5h1393.0 Mobile/09X753 Safari/534.2')
            # chrome_options.add_argument('--incognito')
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
            logging.info('Got driver')
        except Exception as e:
            logging.error('Error getting driver')
            logging.exception('An error occurred')
        return 
    

    # utility functions
    
    @staticmethod
    def _get_hashed_id(string):
        hash_value = hashlib.sha256(string.encode()).hexdigest() # Calculate the SHA-256 hash of the string
        hash_int = int(hash_value, 16) # Convert the hexadecimal hash value to an integer
        truncated_hash = hash_int % (10 ** 18) # Truncate the integer to 20 digits. It has sufficient collision resistance for this use case
        return truncated_hash
    
    @staticmethod
    def _wait_humanly(min_time=10, max_time=15):
        """ Wait a random time between min_time and max_time seconds """
        time_to_sleep = random.uniform(min_time, max_time)
        logging.info(f'Waiting {time_to_sleep} seconds')
        time.sleep(time_to_sleep)
        return
    
    
    # page loading functions

    def _load_page(self, url_to_load):
        """ Load the page """
        try:
            self.driver.get(url)
            logging.info(f'Loaded page: {url_to_load}')
        except Exception as e:
            logging.error('Error loading page')
            logging.exception('An error occurred')
        return

    def _check_page(self, class_to_check):
        """ Check if the page is loaded, based on the presence of a class """
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            logging.info('Page loaded')
        except Exception as e:
            logging.error('Error loading page')
            logging.exception('An error occurred')
        return
    

    # db interaction functions
    
    def _get_row_from_db(self, table, column_list, condition='1=1'):
        """ Get a row from the db """
        try:
            columns = ', '.join(column_list)
            self.cursor.execute(f'select {columns} from {table} where {condition};')
            row = self.cursor.fetchone()
            logging.info(f'Got row from db')
            return row
        except Exception as e:
            logging.error('Error getting row from db')
            logging.exception('An error occurred')
            return
        
    def _insert_or_replace_row(self, table, column_list, value_list):
        """ Insert or replace a row in the db """
        if len(column_list) != len(value_list):
            logging.error('Column list and value list have different lengths')
            return
        try:
            columns = ', '.join(column_list)
            values = ', '.join(value_list)
            self.cursor.execute(f'replace into {table} ({columns}) values ({values});')
            self.connection.commit()
            logging.info(f'Inserted or replaced row in db')
        except Exception as e:
            logging.error('Error inserting or replacing row in db')
            logging.debug(f'Columns: {column_list}')
            logging.debug(f'Values: {value_list}')
            logging.exception('An error occurred')
        return
    

    # run method, to be called from the outside

    def run(self):
        """ Run the iterator. Calls subclass that has to be implemented by the subclass """
        try:
            self._subclass_run()
        except Exception as e:
            logging.error('Error in run')
            logging.exception('An error occurred')
        finally:
            logging.info('Quitting')
            self._wait_humanly()
            self.driver.quit()
            self.connection.close()
        return
    
    def _subclass_run(self):
        """ Placeholder method for subclasses to implement """
        raise NotImplementedError('Subclasses must implement _subclass_run method')
        return