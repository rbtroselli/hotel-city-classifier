import logging
import time
import random
import sqlite3
import hashlib
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import TimeoutException
from langdetect import detect


logging.basicConfig(filename='logs/review_iterator.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

months_short_dict = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
months_long_dict = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}



class ReviewIterator:
    def __init__(self):
        logging.info('Object instantiated')
        self.driver = None
        self.connection = None
        self.cursor = None
        self.continue_flag = True
        self.continue_hotel_flag = True
        self.scraped_reviews_number = 0
        self.hotel_reviews_number = 0
        self.scraped_all_reviews_flag = False
        # review attributes
        self.hotel_id = None
        self.hotel_url = None
        self.review_url = None
        self.review_id = None
        self.review_title = None
        self.review_text = None
        self.review_rating = None
        self.review_month = None
        self.review_year = None
        self.review_month_of_stay = None
        self.review_year_of_stay = None
        self.review_likes = None
        self.review_pics_flag = None
        self.review_language = None
        # review response attributes
        self.review_response_from = None
        self.review_response_text = None
        self.review_response_date = None
        self.review_response_language = None
        # review user attributes
        self.review_user_url = None
        self.review_user_id = None
        self.review_user_name = None
        self.review_user_name_shown = None
        self.review_user_contributions = None
        self.review_user_helpful_votes = None
        self.review_user_location = None
        # other
        self.comment_boxes = None
        self.comment_box = None
        return

    @staticmethod
    def _wait_humanly(min_time=2, max_time=4):
        """ Wait a random time between 2 and 4 seconds """
        time_to_sleep = random.uniform(min_time, max_time)
        logging.info(f'Waiting {time_to_sleep} seconds')
        time.sleep(time_to_sleep)
        return
    
    @staticmethod
    def _get_hashed_id(string):
        # Calculate the SHA-256 hash of the string
        hash_value = hashlib.sha256(string.encode()).hexdigest()
        # Convert the hexadecimal hash value to an integer
        hash_int = int(hash_value, 16)
        # Truncate the integer to 20 digits. It has sufficient collision resistance for this use case
        truncated_hash = hash_int % (10 ** 18)
        return truncated_hash

    def _get_driver(self):
        """ Return a driver to use selenium """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--user-data-dir=./browser/user_data')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled') 
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) # remove "Chrome is being controlled by an automated software"
        self.driver = webdriver.Chrome(options=chrome_options)
        logging.info('Got driver')
        return
    
    def _get_cursor(self):
        """ Get cursor to db """
        self.connection = sqlite3.connect('hotel.db')
        self.cursor = self.connection.cursor()
        logging.info('Got cursor')
        return
    
    def _get_hotel_from_db(self):
        """ Get hotel from db """
        self.cursor.execute('select id, url from result where hotel_scraped_flag=1 and reviews_scraped_flag=0 order by random() limit 1;')
        row = self.cursor.fetchone()
        if row is not None:
            self.hotel_id, self.hotel_url = row
            logging.info(f'Got hotel from db')
            logging.info(f'Hotel id: {self.hotel_id}')
            logging.info(f'Hotel url: {self.hotel_url}')
            return
        else:
            self.continue_flag = False
            logging.info('No more reviews to scrape')
            return
        
    def _check_hotel_page(self):
        """ Check if hotel page is valid """
        if self.driver.find_elements('class name', 'WMndO.f') == []:
            raise Exception('No name found, invalid page')
        logging.info('Checked page')
        return
    
    def _get_hotel_page(self):
        """ Get hotel page """
        self.driver.get(self.hotel_url)
        logging.info('Got page')
        return
    
    def _load_hotel_page(self):
        """ Get hotel page, and check if valid. Catch exceptions and retry up to 10 times """
        retries = 0
        while retries < 3:
            try:
                self._get_hotel_page()
                self._check_hotel_page()
                logging.info('Loaded hotel page')
                self._wait_humanly()
                break
            except Exception as e:
                retries += 1
                logging.error(e)
                logging.error(f'Did not load hotel page, retry {retries}')
                logging.exception('An error occurred')
                self._wait_humanly()
                continue
        return
    
    
    def _reset_attributes(self):
        """ Reset attributes to None """
        self.scraped_reviews_number = 0
        self.hotel_reviews_number = 0
        self.scraped_all_reviews_flag = False
        # review
        self.review_url = None
        self.review_id = None
        self.review_title = None
        self.review_text = None
        self.review_rating = None
        self.review_month = None
        self.review_year = None
        self.review_month_of_stay = None
        self.review_year_of_stay = None
        self.review_likes = None
        self.review_pics_flag = None
        self.review_language = None
        # review response
        self.review_response_from = None
        self.review_response_text = None
        self.review_response_date = None
        self.review_response_language = None
        # review user
        self.review_user_url = None
        self.review_user_id = None
        self.review_user_name = None
        self.review_user_name_shown = None
        self.review_user_contributions = None
        self.review_user_helpful_votes = None
        self.review_user_location = None
        logging.info('Reset attributes')
        return
    
    def _scrape_review(self):
        """ Scrape single review """
        # review
        self.review_url = self.comment_box.find_element('class name', 'joSMp.MI._S.b.S6.H5.Cj._a').find_element('class name', 'BMQDV._F.Gv.wSSLS.SwZTJ').get_attribute('href')
        self.review_id = self._get_hashed_id(self.review_url)
        self.review_title = self.comment_box.find_element('class name', 'JbGkU.Cj').text
        self.review_text = self.comment_box.find_element('class name', 'orRIx.Ci._a.C').text
        self.review_rating = self.comment_box.find_element('class name', 'IaVba.F1').text.split(' ')[0]
        if 'today' in self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower():
            review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower()
            self.review_month = time.strftime('%m')
            self.review_year = time.strftime('%Y')
        elif 'yesterday' in self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower():
            review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower()
            yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
            self.review_month = yesterday.split('-')[1]
            self.review_year = yesterday.split('-')[0]
        else:
            review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text # only print for check
            self.review_month = months_short_dict[self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.split(' ')[-2].lower()]
            self.review_year = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.split(' ')[-1]
        review_date_of_stay = self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text if self.comment_box.find_elements('class name', 'iSNGb._R.Me.S4.H3.Cj') != [] else 'NA'
        self.review_month_of_stay = months_long_dict[self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text.split(': ')[-1].split(' ')[-2].lower()] if self.comment_box.find_elements('class name', 'iSNGb._R.Me.S4.H3.Cj') != [] else -1
        self.review_year_of_stay = self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text.split(': ')[-1].split(' ')[-1] if self.comment_box.find_elements('class name', 'iSNGb._R.Me.S4.H3.Cj') != [] else -1
        self.review_likes = self.comment_box.find_element('class name', 'biGQs._P.FwFXZ').text
        self.review_pics_flag = True if self.comment_box.find_elements('class name', 'Ctnpg._T.lqJaB') != [] else False
        self.review_language = detect(self.review_text)
        # review response
        self.review_response_from = self.comment_box.find_element('class name', 'MFqgB').text if self.comment_box.find_elements('class name', 'MFqgB') else None
        self.review_response_text = self.comment_box.find_element('class name', 'XCFtd').text if self.comment_box.find_elements('class name', 'XCFtd') else None
        self.review_response_date = self.comment_box.find_element('class name', 'vijoR').get_attribute('title') if self.comment_box.find_elements('class name', 'vijoR') else None
        self.review_response_language = detect(self.review_response_text) if self.review_response_text else None
        # review user
        self.review_user_url = self.comment_box.find_element('class name', 'MjDLG.VKCbE').get_attribute('href')
        self.review_user_id = self._get_hashed_id(self.review_user_url)
        self.review_user_name = self.comment_box.find_element('class name', 'MjDLG.VKCbE').get_attribute('href').split('Profile/')[-1]
        self.review_user_name_shown = self.comment_box.find_element('class name', 'MjDLG.VKCbE').text
        for review_user_info in self.comment_box.find_elements('class name', 'sIZXw.S2.H2.Ch.d'):
            if 'contribution' in review_user_info.text:
                self.review_user_contributions = review_user_info.text.split(' ')[0].replace(',', '')
            elif 'helpful vote' in review_user_info.text:
                self.review_user_helpful_votes = review_user_info.text.split(' ')[0].replace(',', '')
            else:
                self.review_user_location = review_user_info.text
        # hotel
        logging.info(f'Hotel url: {self.hotel_url}')
        # review
        logging.info(f'Review url: {self.review_url}')
        logging.info(f'Review id: {self.review_id}')
        logging.info(f'Review title: {self.review_title}')
        logging.info(f'Review text: {self.review_text[:30]} [...] {self.review_text[-30:]}')
        logging.info(f'Review rating: {self.review_rating}')
        logging.info(f'Review date [only as a check]: {review_date}')
        logging.info(f'Review month: {self.review_month}')
        logging.info(f'Review year: {self.review_year}')
        logging.info(f'Review date of stay [only as a check]: {review_date_of_stay}')
        logging.info(f'Review month of stay: {self.review_month_of_stay}')
        logging.info(f'Review year of stay: {self.review_year_of_stay}')
        logging.info(f'Review likes: {self.review_likes}')
        logging.info(f'Review pics flag: {self.review_pics_flag}')
        logging.info(f'Review language: {self.review_language}')
        # review response
        logging.info(f'Review response from: {self.review_response_from}')
        logging.info(f'Review response text: {self.review_response_text[:30] if self.review_response_text is not None else None} [...] {self.review_response_text[-30:] if self.review_response_text is not None else None}')
        logging.info(f'Review response date: {self.review_response_date}')
        logging.info(f'Review response language: {self.review_response_language}')
        # review user
        logging.info(f'Review user url: {self.review_user_url}')
        logging.info(f'Review user id: {self.review_user_id}')
        logging.info(f'Review user name: {self.review_user_name}')
        logging.info(f'Review user name shown: {self.review_user_name_shown}')
        logging.info(f'Review user contributions: {self.review_user_contributions}')
        logging.info(f'Review user helpful votes: {self.review_user_helpful_votes}')
        logging.info(f'Review user location: {self.review_user_location}')
        logging.info('Scraped review')
        return
    
    def _delete_insert_review(self):
        """ Insert review into db """
        self.cursor.execute(f'delete from REVIEW where id={self.review_id}')
        self.cursor.execute(f"""
            insert into REVIEW (
                id, url, title, text, rating, month_of_review, year_of_review, month_of_stay, 
                year_of_stay, likes, pics_flag, language, response_from, response_text, 
                response_date, response_language, user_id, hotel_id
            )
            values (
                {self.review_id},
                '{self.review_url}',
                '{self.review_title.replace("'","''")}',
                '{self.review_text.replace("'","''")}',
                {self.review_rating},
                {self.review_month},
                {self.review_year},
                {self.review_month_of_stay},
                {self.review_year_of_stay},
                {self.review_likes},
                {self.review_pics_flag},
                '{self.review_language}',
                '{self.review_response_from.replace("'","''") if self.review_response_from is not None else 'NA'}',
                '{self.review_response_text.replace("'","''") if self.review_response_text is not None else 'NA'}',
                '{self.review_response_date if self.review_response_date is not None else 'NA'}',
                '{self.review_response_language if self.review_response_language is not None else 'NA'}',
                {self.review_user_id},
                {self.hotel_id}
            );
        """)
        # self.connection.commit()
        logging.info('Deleted-inserted review. Did not commit yet')
        return
    
    def _delete_insert_review_user(self):
        """ Insert review into db """
        self.cursor.execute(f'delete from USER where id={self.review_user_id}')
        self.cursor.execute(f"""
            insert into USER (
                id, url, name, name_shown, contributions, helpful_votes, location
            )
            values (
                {self.review_user_id},
                '{self.review_user_url}',
                '{self.review_user_name.replace("'","''")}',
                '{self.review_user_name_shown.replace("'","''")}',
                {self.review_user_contributions if self.review_user_contributions is not None else -1},
                {self.review_user_helpful_votes if self.review_user_helpful_votes is not None else -1},
                '{self.review_user_location.replace("'","''") if self.review_user_location is not None else 'NA'}'
            );
        """)
        # self.connection.commit()
        logging.info('Deleted-inserted review user. Did not commit yet')
        return
    
    def _scrape_review_page(self):
        """ Scrape the review page """
        self.comment_boxes = self.driver.find_elements('class name', 'azLzJ.MI.Gi.z.Z.BB.kYVoW')
        for self.comment_box in self.comment_boxes:
            self._scrape_review()
            self._delete_insert_review()
            self._delete_insert_review_user()
            self._reset_attributes()
            logging.info('-'*50)
        self.connection.commit()
        logging.info('Scraped review page. Committed reviews and users delete-inserts to db')
        return


    def _increase_page(self):
        """ Increase page. If button not found, set continue_hotel_flag to False, to step to next hotel """
        i = 0
        while i < 3:
            try:
                wait = WebDriverWait(self.driver, 0.5)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next page']"))).click()
                logging.info('Clicked Next Page button')
                self._wait_humanly(3,3) # wait flat time to avoid missing elements. del-insert of page reviews already takes a variable time of 2-3 seconds
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'azLzJ.MI.Gi.z.Z.BB.kYVoW'))) # wait for comment boxes to load
                # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'joSMp.MI._S.b.S6.H5.Cj._a'))) # wait for review urls to load
                # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'MjDLG.VKCbE'))) # wait for review user urls to load
                self.continue_hotel_flag = True
                break
            except TimeoutException:
                i += 1
                logging.info(f'Next page button not found, retry: {i}')
                self.continue_hotel_flag = False
                continue
            except Exception as e:
                i += 1
                logging.error(e)
                logging.error('Error')
                logging.exception('An error occurred')
                self._wait_humanly()
                self.continue_hotel_flag = False
                continue
        return

    def _push_all_languages_button(self):
        """ Click on 'All languages' button. Retry up to 10 times """
        i = 0
        all_languages_button = self.driver.find_element('xpath', "//span[contains(text(),'All languages')]")
        while i < 10:
            try:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.element_to_be_clickable(all_languages_button)).click()
                logging.info('Clicked All languages button')
                self._wait_humanly()
                break
            except Exception as e:
                i += 1
                logging.error(e)
                logging.error('All languages button not found')
                logging.exception('An error occurred')
                self._wait_humanly()
                continue
        return

    def _get_hotel_reviews_number(self):
        """ Get hotel reviews number, to check if they've been taken all before finishing and updating flag """
        self.hotel_reviews_number = int(self.driver.find_element('class name', 'hvAtG').text.split(' ')[0].replace(',', ''))
        logging.info(f'Hotel reviews number: {self.hotel_reviews_number}')
        return

    def _update_reviews_flag(self):
        """ Update reviews flag in db """
        self.cursor.execute(f"""
            update result
            set reviews_scraped_flag=1
            where id={self.hotel_id}
        """)
        self.connection.commit()
        logging.info('Updated reviews flag')
        return
    
    def _check_scraped_reviews_number(self):
        """ Check if the number of scraped reviews match the number of reviews in the page. Add a buffer of 10 reviews, the site number may not be up to date yet """
        self.scraped_reviews_number = self.cursor.execute(f'select count(*) from REVIEW where hotel_id={self.hotel_id}').fetchone()[0]
        logging.info(f'Scraped reviews number: {self.scraped_reviews_number}')
        if (self.scraped_reviews_number >= self.hotel_reviews_number and self.scraped_reviews_number <= self.hotel_reviews_number + 10):
            self.scraped_all_reviews_flag = True
        else:
            self.scraped_all_reviews_flag = False
        logging.info(f'Checked scraped reviews number. Scraped all reviews: {self.scraped_all_reviews_flag}')
        return


    def _iterate_reviews_pages(self):
        """ Iterate through reviews pages """
        while self.continue_hotel_flag == True:
            self._scrape_review_page()
            self._increase_page()
        logging.info('Iterated all reviews pages for the hotel. Going to next hotel')
        return
    
    def _iterate_hotels(self):
        """ Get hotel from db, setup the first page, and start iterating through reviews pages. Update flag at the end """
        while True:
            try:
                self.continue_hotel_flag = True
                self._get_hotel_from_db()
                if self.continue_flag == False:
                    break
                self._load_hotel_page()
                self._push_all_languages_button()
                self._iterate_reviews_pages()
                self._get_hotel_reviews_number()
                self._check_scraped_reviews_number()
                if self.scraped_all_reviews_flag == False:
                    raise Exception('Missing reviews for the hotel, skipping to next hotel')
                self._update_reviews_flag()
            except Exception as e:
                logging.error(e)
                logging.error('Error in hotel, skipping to next hotel')
                logging.exception('An error occurred')
                self._wait_humanly()
                continue
        logging.info('Iterated all hotels. Done')
        return


    def run(self):
        """ Run the search iterator """
        try:
            self._get_driver()
            self._get_cursor()
            self._iterate_hotels()
        except Exception as e:
            logging.error(e)
            logging.error('Error in run')
            logging.exception('An error occurred')
            raise e
        finally:
            logging.info('Quitting')
            self._wait_humanly()
            self.driver.quit()
            self.connection.close()
        return

if __name__ == '__main__':
    ri = ReviewIterator()
    ri.run()
