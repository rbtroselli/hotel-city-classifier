import logging # settings inherited from base_iterator
from base_iterator import BaseIterator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 




class ResultIterator(BaseIterator):
    """ Iterator to scrape search results """
    url_template = 'https://www.tripadvisor.com/Hotels-g187791-oa{}-Rome_Lazio-Hotels.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # pass all arguments to parent class
        self.continue_flag = False
        self.continue_flag_retries = 0
        self.page_number = -1
        # attributes (manage with a dictionary?)
        self.result_element = None
        self.result_url = None
        self.result_rating = None
        self.result_reviews = None
        self.result_sponsored_flag = False
        self.result_rank = None
        self.result_id = None
        self.result_element = None
        logging.info('Completed subclass initialization')
        logging.info(self.url_template)
        return
    
    def _increase_page(self):
        """ Increase page number """
        self.page_number += 1
        self.url = ResultIterator.url_template.format(self.page_number*30)
        logging.info(f'Page increased: {self.page_number}, url: {self.url}')
        return
    
    def _decrease_page(self):
        """ Decrease page number """
        self.page_number -= 1
        self.url = ResultIterator.url_template.format(self.page_number*30)
        logging.info(f'Page decreased: {self.page_number}, url: {self.url}')
        return
    
    def _click_seeall_button(self):
        """ Click on 'See all' button """
        wait = WebDriverWait(self.driver, 50)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'See all')]"))).click()
        logging.info('Clicked See all button')
        return

    def _continue_not_stop(self):
        """ 
        Decide if continue or stop scraping. 
        If continue_flag is False, retry loading page. If retries >= 10, stop scraping
        If continue_flag is True, reset retries and continue to next page
        """
        if (self.continue_flag == False) and (self.continue_flag_retries < 5):
            self.continue_flag_retries += 1
            self._decrease_page()
            logging.info(f'continue_flag is False, retrying loading page, retry {self.continue_flag_retries}')
            return True
        if (self.continue_flag == False) and (self.continue_flag_retries >= 10):
            logging.info('continue_flag is False, breaking scraping loop')
            return False
        else: # continue_flag is True
            self.continue_flag_retries = 0 # reset retries
            self.continue_flag = False # reset flag, to be set to True if there are new results
            logging.info('Done page, continuing to next page')
            logging.info('-'*50)
            return True

    def _scrape_result(self):
        """ Scrape result element """
        self.result_url = self.result_element.find_element('class name', 'BMQDV._F.Gv.wSSLS.SwZTJ.FGwzt.ukgoS').get_attribute('href').split('?')[0]
        self.result_reviews = self.result_element.find_element('class name', 'luFhX.o.W.f.u.w.JSdbl').get_attribute('aria-label').split(' ')[-2].replace(',', '')
        self.result_rating = self.result_element.find_element('class name', 'luFhX.o.W.f.u.w.JSdbl').get_attribute('aria-label').split(' ')[0] if self.result_reviews != '0' else -1
        self.result_sponsored_flag = self.result_element.find_elements('class name', 'ngpKT.WywIO') != []
        self.result_rank = self.result_element.find_element('class name', 'nBrpc.Wd.o.W').text.split(' ')[0].replace('.', '') if self.result_sponsored_flag == False else -1
        self.result_id = self._get_hashed_id(self.result_url)
        logging.info(f'Scraped result')
        logging.info(f'Id: {self.result_id}')
        logging.info(f'URL: {self.result_url}')
        logging.info(f'Rating: {self.result_rating}')
        logging.info(f'Reviews: {self.result_reviews}')
        logging.info(f'Sponsored: {self.result_sponsored_flag}')
        logging.info(f'Position: {self.result_rank}')
        return

    def _check_if_new_result(self):
        """ Check if result is already in db, change new_result_flag if so """
        if self.cursor.execute(f'select count(*)>0 from RESULT where id={self.result_id}').fetchone()[0]: # id already in db
            self.new_result_flag = False
            logging.info('Set new_result_flag to False')
        else:
            self.new_result_flag = True
            logging.info('Set new_result_flag to True')
        return
    
    def _update_continue_flag(self):
        """ 
        Set continue_flag to True if there are new results. 
        At least one new result in the page = continue page iteration. No new results in page = stop page iteration 
        """
        if (self.new_result_flag == True and self.continue_flag == False):
            self.continue_flag = True
            logging.info('Set continue_flag to True')
        return
    
    def _sub_iterate_result(self):
        """ Iterate over search results in the page """
        for self.result_element in self.driver.find_elements('class name', 'listItem'):
            self._scrape_result()
            self._check_if_new_result()
            if self.result_sponsored_flag == True:
                logging.info('Sponsored result, skipping')
                continue
            self._insert_replace_row(
                table='RESULT', 
                column_list=['id', 'rating', 'reviews', 'url', 'page', 'rank'], 
                value_list=[self.result_id, self.result_rating, self.result_reviews, self.result_url, self.page_number, self.result_rank]
            ) # a dict can be used instead of lists. self.result_dict. Keys are column names, values are values
            self._update_continue_flag()
        logging.info('Iterated all results')
        return
    

    # page setup (get page, click button)

    def _setup_page(self):
        """ Get page and click on 'See all' button. Retries implemented """
        retries = 0
        while retries < 5:
            try:
                self._get_page()
                self._wait_humanly()
                self._click_seeall_button()
                self._wait_humanly()
                # self._check_page()
                logging.info('Loaded page')
                break
            except Exception as e:
                retries += 1
                logging.error(f'Page not loaded: error getting page or clicking button, retry {retries}')
                logging.exception('An error occurred')
                self._wait_humanly()
                continue        
        return
    

    # run method (pages iteration)

    def _subclass_run(self):
        """ Iterate over search results pages"""
        while True:
            self._increase_page()
            self._setup_page()
            self._sub_iterate_result()
            if self._continue_not_stop() is False: 
                break
        return