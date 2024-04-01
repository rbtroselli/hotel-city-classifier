import logging # settings inherited from base_iterator
import time
from base_iterator import BaseIterator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from langdetect import detect





class ReviewIterator(BaseIterator):
    """ Iterator to scrape reviews """
    months_short_dict = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
    months_long_dict = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.continue_hotel_flag = True
        self.hotel_id = None
        self.hotel_url = None
        self.hotel_page_reviews_number = None
        self.hotel_scraped_reviews_number = None
        self.comment_box = None
        self.skip_review_flag = False
        # attributes that go in the db
        self.review_dict = {
            'id': None,
            'url': None,
            'title': None,
            'text': None,
            'rating': None,
            'month_of_review': None,
            'year_of_review': None,
            'month_of_stay': None,
            'year_of_stay': None,
            'likes': None,
            'pics_flag': None,
            'language': None,
            'response_from': None,
            'response_text': None,
            'response_date': None,
            'response_language': None,
            'user_id': None,
            'hotel_id': None
        }
        self.user_dict = {
            'id': None,
            'url': None,
            'name': None,
            'name_shown': None,
            'contributions': None,
            'helpful_votes': None,
            'location': None
        }
        logging.info('Completed subclass initialization')
        return
    




    # get hotel reviews number and scraped reviews number, to compare and check if all reviews are scraped

    def _get_hotel_page_reviews_number(self):
        """ Get hotel reviews number, to check if they've been taken all before finishing and updating flag """
        self.hotel_page_reviews_number = int(self.driver.find_element('class name', 'hvAtG').text.split(' ')[0].replace(',', ''))
        logging.info(f'Hotel page reviews number: {self.hotel_page_reviews_number}')
        return
    
    def _get_hotel_scraped_reviews_number(self):
        """ Get hotel scraped reviews number from db """
        self.hotel_scraped_reviews_number = self.cursor.execute(f'select count(*) from REVIEW where hotel_id={self.hotel_id}').fetchone()[0]
        logging.info(f'Hotel scraped reviews number: {self.hotel_scraped_reviews_number}')
        return





    # actual scraping

    def _increase_review_page(self):
        """ Increase page. If button not found, set continue_hotel_flag to False, to go to next hotel """
        retries = 0
        while retries < 3:
            try:
                wait = WebDriverWait(self.driver, 0.5)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next page']"))).click()
                logging.info('Clicked Next Page button')
                self._wait_humanly()
                self._check_page(class_to_check='azLzJ.MI.Gi.z.Z.BB.kYVoW') # wait for comment boxes to load
                self.continue_hotel_flag = True # reset flag to True when button is pressed
                break
            except TimeoutException:
                retries += 1
                logging.info(f'Next page button not found, retry: {retries}')
                self.continue_hotel_flag = False # set flag to False when button is not found
                continue
            except Exception as e:
                retries += 1
                logging.error('Error')
                logging.exception('An error occurred')
                self._wait_humanly()
                self.continue_hotel_flag = False # set flag to False when an error occurs
                continue
        return

    def _scrape_single_review(self):
        """ Scrape single review """
        # review
        try:
            self.review_dict['url'] = self.comment_box.find_element('class name', 'joSMp.MI._S.b.S6.H5.Cj._a').find_element('class name', 'BMQDV._F.Gv.wSSLS.SwZTJ').get_attribute('href')
            self.review_dict['id'] = self._get_hashed_id(self.review_dict['url'])
            self.review_dict['title'] = self.comment_box.find_element('class name', 'JbGkU.Cj').text
            self.review_dict['text'] = self.comment_box.find_element('class name', 'orRIx.Ci._a.C').text
            self.review_dict['rating'] = self.comment_box.find_element('class name', 'IaVba.F1').text.split(' ')[0]
            if 'today' in self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower():
                review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower()
                self.review_dict['month_of_review'] = time.strftime('%m')
                self.review_dict['year_of_review'] = time.strftime('%Y')
            elif 'yesterday' in self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower():
                review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower()
                yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
                self.review_dict['month_of_review'] = yesterday.split('-')[1]
                self.review_dict['year_of_review'] = yesterday.split('-')[0]
            else: # standard case, month and year
                review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text
                self.review_dict['month_of_review'] = ReviewIterator.months_short_dict[self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.split(' ')[-2].lower()]
                self.review_dict['year_of_review'] = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.split(' ')[-1]
                if int(self.review_dict['year_of_review']) < 2000: # if year is less than 2000, the scraper got the day of the month. It happens when the review is from the current month, so set the year to current year
                    self.review_dict['year_of_review'] = time.strftime('%Y')
            review_date_of_stay = self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text if self.comment_box.find_elements('class name', 'iSNGb._R.Me.S4.H3.Cj') != [] else 'NA'
            self.review_dict['month_of_stay'] = ReviewIterator.months_long_dict[self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text.split(': ')[-1].split(' ')[-2].lower()] if self.comment_box.find_elements('class name', 'iSNGb._R.Me.S4.H3.Cj') != [] else -1
            self.review_dict['year_of_stay'] = self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text.split(': ')[-1].split(' ')[-1] if self.comment_box.find_elements('class name', 'iSNGb._R.Me.S4.H3.Cj') != [] else -1
            self.review_dict['likes'] = self.comment_box.find_element('class name', 'biGQs._P.FwFXZ').text
            self.review_dict['pics_flag'] = True if self.comment_box.find_elements('class name', 'Ctnpg._T.lqJaB') != [] else False
            self.review_dict['language'] = detect(self.review_dict['text'])
            # review response
            self.review_dict['response_from'] = self.comment_box.find_element('class name', 'MFqgB').text if self.comment_box.find_elements('class name', 'MFqgB') else None
            self.review_dict['response_text'] = self.comment_box.find_element('class name', 'XCFtd').text if self.comment_box.find_elements('class name', 'XCFtd') else None
            self.review_dict['response_date'] = self.comment_box.find_element('class name', 'vijoR').get_attribute('title') if self.comment_box.find_elements('class name', 'vijoR') else None
            self.review_dict['response_language'] = detect(self.review_dict['response_text']) if self.review_dict['response_text'] else None
            # review user
            self.user_dict['url'] = self.comment_box.find_element('class name', 'MjDLG.VKCbE').get_attribute('href')
            self.user_dict['id'] = self._get_hashed_id(self.user_dict['url'])
            self.user_dict['name'] = self.comment_box.find_element('class name', 'MjDLG.VKCbE').get_attribute('href').split('Profile/')[-1]
            self.user_dict['name_shown'] = self.comment_box.find_element('class name', 'MjDLG.VKCbE').text
            for review_user_info in self.comment_box.find_elements('class name', 'sIZXw.S2.H2.Ch.d'):
                if 'contribution' in review_user_info.text:
                    self.user_dict['contributions'] = review_user_info.text.split(' ')[0].replace(',', '')
                elif 'helpful vote' in review_user_info.text:
                    self.user_dict['helpful_votes'] = review_user_info.text.split(' ')[0].replace(',', '')
                else:
                    self.user_dict['location'] = review_user_info.text
            self.review_dict['user_id'] = self.user_dict['id']
            self.review_dict['hotel_id'] = self.hotel_id
            # log
            logging.info('Scraped review and user')
            for dictionary in [self.review_dict, self.user_dict]:
                for key, value in dictionary.items():
                    if 'text' in str(key) and value is not None:
                        value_str = str(value)[:50] + ' [...] ' + str(value)[-50:] # Truncate string in log
                    else:
                        value_str = value
                    logging.info(f'{key}: {value_str}')
        except Exception as e:
            self.skip_review_flag = True # Do not insert if there is an error
            self.continue_hotel_flag = False # Do not continue with the hotel either if there is an error
            logging.error('Error scraping review')
            logging.exception('An error occurred')
        return

    def _scrape_review_page(self):
        """ Scrape the review page """
        try: # catch errors for not loading comment boxes (not caught in the inner functions)
            self._check_page(class_to_check='azLzJ.MI.Gi.z.Z.BB.kYVoW') # wait for comment boxes to load
            comment_boxes = self.driver.find_elements('class name', 'azLzJ.MI.Gi.z.Z.BB.kYVoW')
            for self.comment_box in comment_boxes:
                self._reset_dict(self.review_dict)
                self._reset_dict(self.user_dict)
                self.skip_review_flag = False # reset
                self._scrape_single_review()
                if self.skip_review_flag == True: # do not insert the review
                    continue
                self._insert_replace_row(table='REVIEW', column_value_dict=self.review_dict, commit=False)
                self._insert_replace_row(table='USER', column_value_dict=self.user_dict, commit=False)
                logging.info('-'*50)
            self.connection.commit() # commit the whole page at the end
            logging.info('Scraped review page. Committed reviews and users insert or replace to db')
        except Exception as e:
            logging.error('Error scraping review page')
            logging.exception('An error occurred')
            self.continue_hotel_flag = False # Go to next hotel if an error occurs
        return

    def _sub_iterate_reviews_pages(self):
        """ Iterate over reviews pages """
        while self.continue_hotel_flag == True:
            self._scrape_review_page()
            self._increase_review_page()
        logging.info('Iterated all reviews pages for the hotel. Going to next hotel')
        return





    # page setup (get page, and check it). Also click on 'All languages' button

    def _setup_page(self):
        """ Get page and check it. Retries implemented """
        self.url = self.hotel_url
        retries = 0
        while retries < 5:
            try:
                self._get_page()
                self._check_page(class_to_check='WMndO.f') # check presence of element
                self._wait_humanly()
                logging.info('Setup page')
                break
            except Exception as e:
                retries += 1
                logging.error(f'Page not setup: error getting page, retry {retries}')
                logging.exception('An error occurred')
                self._wait_humanly()
                continue        
        return
    
    def _push_all_languages_button(self):
        """ Click on 'All languages' button. Retries implemented """
        retries = 0
        while retries < 5:
            try:
                all_languages_button = self.driver.find_element('xpath', "//span[contains(text(),'All languages')]")
                wait = WebDriverWait(self.driver, 5)
                wait.until(EC.element_to_be_clickable(all_languages_button)).click()
                logging.info('Clicked All languages button')
                self._wait_humanly()
                break
            except Exception as e:
                retries += 1
                logging.error(f'Error clicking All languages button, retry {retries}')
                logging.exception('An error occurred')
                self._wait_humanly()
                continue
        return 





    # run method (pages iteration)

    def _subclass_run(self):
        """ Iterate over hotel pages """
        while True:
            self.continue_hotel_flag = True # reset flag
            self.hotel_id, self.hotel_url = self._get_row_from_db(table='RESULT', column_list=['id', 'url'], condition='hotel_scraped_flag=1 and reviews_scraped_flag=0')
            if (self.hotel_id == None and self.hotel_url == None): # no more hotels to scrape reviews of
                break
            self._setup_page()
            self._push_all_languages_button()
            self._sub_iterate_reviews_pages()
            self._get_hotel_page_reviews_number()
            self._get_hotel_scraped_reviews_number()
            if (self.hotel_scraped_reviews_number < self.hotel_page_reviews_number or self.hotel_scraped_reviews_number > self.hotel_page_reviews_number + 10):
                logging.error('Missing reviews for the hotel, skipping to next hotel without updating the reviews flag')
                continue
            self._update_flag(table='RESULT', column='reviews_scraped_flag', value=True, condition=f'id={self.hotel_id}')
        logging.info('Iterated all hotels. Done')
        return