import logging
import time
import random
import sqlite3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from langdetect import detect


# logging.basicConfig(filename='logs/review_iterator.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

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
        # review attributes
        self.hotel_id = None
        self.hotel_url = None
        self.review_url = None
        self.review_id = None
        self.review_title = None
        self.review_text = None
        self.review_rating = None
        self.review_year_of_stay = None
        self.review_month_of_stay = None
        self.review_likes = None
        self.review_pics_flag = None
        self.review_language = None
        self.review_month = None
        self.review_year = None
        # review response attributes
        self.review_response_from = None
        self.review_response_text = None
        self.review_response_date = None
        self.revuew_response_language = None
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
    def _wait_humanly():
        """ Wait a random time between 10 and 20 seconds """
        time_to_sleep = random.uniform(5, 15)
        logging.info(f'Waiting {time_to_sleep} seconds')
        time.sleep(time_to_sleep)
        return

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
    
    def _get_hotel_from_db(self):
        """ Get hotel from db """
        self.cursor.execute('select id, url from result where reviews<100 and hotel_scraped_flag=1 and reviews_scraped_flag=0 order by random() limit 1;')
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
        while retries < 10:
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
                self._wait_humanly()
                continue
        return
    
    
    def _reset_attributes(self):
        """ Reset attributes to None """
        # review
        self.review_url = None
        self.review_id = None
        self.review_title = None
        self.review_text = None
        self.review_rating = None
        self.review_year_of_stay = None
        self.review_month_of_stay = None
        self.review_likes = None
        self.review_pics_flag = None
        self.review_language = None
        self.review_month = None
        self.review_year = None
        # review response
        self.review_response_from = None
        self.review_response_text = None
        self.review_response_date = None
        self.revuew_response_language = None
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
        self.review_id = abs(hash(self.review_url))
        self.review_title = self.comment_box.find_element('class name', 'JbGkU.Cj').text
        self.review_text = self.comment_box.find_element('class name', 'orRIx.Ci._a.C').text
        self.review_rating = self.comment_box.find_element('class name', 'IaVba.F1').text.split(' ')[0]
        review_date_of_stay = self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text # only print for check
        self.review_year_of_stay = self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text.split(': ')[-1].split(' ')[-1]
        self.review_month_of_stay = months_long_dict[self.comment_box.find_element('class name', 'iSNGb._R.Me.S4.H3.Cj').text.split(': ')[-1].split(' ')[-2].lower()]
        self.review_likes = self.comment_box.find_element('class name', 'biGQs._P.FwFXZ').text
        self.review_pics_flag = True if self.comment_box.find_elements('class name', 'Ctnpg._T.lqJaB') != [] else False
        self.review_language = detect(self.review_text)
        if 'today' in self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower():
            review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.lower()
            self.review_month = time.strftime('%m')
            self.review_year = time.strftime('%Y')
        else:
            review_date = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text # only print for check
            self.review_month = months_short_dict[self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.split(' ')[-2].lower()]
            self.review_year = self.comment_box.find_element('class name', 'ScwkD._Z.o.S4.H3.Ci').text.split(' ')[-1]
        # review response
        self.review_response_from = self.comment_box.find_element('class name', 'MFqgB').text if self.comment_box.find_elements('class name', 'MFqgB') else None
        self.review_response_text = self.comment_box.find_element('class name', 'XCFtd').text if self.comment_box.find_elements('class name', 'XCFtd') else None
        self.review_response_date = self.comment_box.find_element('class name', 'vijoR').get_attribute('title') if self.comment_box.find_elements('class name', 'vijoR') else None
        self.revuew_response_language = detect(self.review_response_text) if self.review_response_text else None
        # review user
        self.review_user_url = self.comment_box.find_element('class name', 'MjDLG.VKCbE').get_attribute('href')
        self.review_user_id = abs(hash(self.review_user_url))
        self.review_user_name = self.comment_box.find_element('class name', 'MjDLG.VKCbE').get_attribute('href').split('Profile/')[-1]
        self.review_user_name_shown = self.comment_box.find_element('class name', 'MjDLG.VKCbE').text
        for review_user_info in self.comment_box.find_elements('class name', 'sIZXw.S2.H2.Ch.d'):
            if 'contributions' in review_user_info.text:
                self.review_user_contributions = review_user_info.text.split(' ')[0].replace(',', '')
            elif 'helpful votes' in review_user_info.text:
                self.review_user_helpful_votes = review_user_info.text.split(' ')[0].replace(',', '')
            else:
                self.review_user_location = review_user_info.text
        # review
        logging.info(f'Review url: {self.review_url}')
        logging.info(f'Review id: {self.review_id}')
        logging.info(f'Review title: {self.review_title}')
        logging.info(f'Review text: {self.review_text}')
        logging.info(f'Review rating: {self.review_rating}')
        logging.info(f'Review date of stay [only as a check]: {review_date_of_stay}')
        logging.info(f'Review year of stay: {self.review_year_of_stay}')
        logging.info(f'Review month of stay: {self.review_month_of_stay}')
        logging.info(f'Review likes: {self.review_likes}')
        logging.info(f'Review pics flag: {self.review_pics_flag}')
        logging.info(f'Review language: {self.review_language}')
        logging.info(f'Review date [only as a check]: {review_date}')
        logging.info(f'Review month: {self.review_month}')
        logging.info(f'Review year: {self.review_year}')
        # review response
        logging.info(f'Review response from: {self.review_response_from}')
        logging.info(f'Review response text: {self.review_response_text}')
        logging.info(f'Review response date: {self.review_response_date}')
        logging.info(f'Review response language: {self.revuew_response_language}')
        # review user
        logging.info(f'Review user url: {self.review_user_url}')
        logging.info(f'Review user id: {self.review_user_id}')
        logging.info(f'Review user name: {self.review_user_name}')
        logging.info(f'Review user name shown: {self.review_user_name_shown}')
        logging.info(f'Review user contributions: {self.review_user_contributions}')
        logging.info(f'Review user helpful votes: {self.review_user_helpful_votes}')
        logging.info(f'Review user location: {self.review_user_location}')
        logging.info('Scraped review')
        logging.info('-'*50)
        return
    
    def _insert_review(self):
        """ Insert review into db """
        return
        self.cursor.execute(f"""

        """)
        self.connection.commit()
        logging.info('Inserted review')
        return
    
    def _insert_review_user(self):
        """ Insert review into db """
        return
        self.cursor.execute(f"""
            
        """)
        self.connection.commit()
        logging.info('Inserted review')
        return
    

    
    def _scrape_review_page(self):
        """ Scrape the review page """
        self.comment_boxes = self.driver.find_elements('class name', 'azLzJ.MI.Gi.z.Z.BB.kYVoW')
        for self.comment_box in self.comment_boxes:
            self._scrape_review()
            self._insert_review()
            self._insert_review_user()
            self._reset_attributes()
        logging.info('Scraped review page')
        return


    def _increase_page(self):
        """ Increase page. If button not found, set continue_hotel_flag to False, to step to next hotel """
        i = 0
        while i < 3:
            try:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next page']"))).click()
                logging.info('Clicked Next Page button')
                self._wait_humanly()
                self._continue_hotel_flag = True
                break
            except Exception as e:
                i += 1
                logging.error(e)
                logging.error('Next page button not found')
                self._wait_humanly()
                self._continue_hotel_flag = False
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
                self._wait_humanly()
                continue
        return

    def _update_reviews_flag(self):
        """ Update reviews flag in db """
        # self.cursor.execute(f"""
        #     update result
        #     set reviews_scraped_flag=1
        #     where id={self.hotel_id}
        # """)
        self.cursor.execute('select 1') # test
        self.connection.commit()
        logging.info('Updated reviews flag')
        return


    def _iterate_reviews_pages(self):
        """ Iterate through reviews pages """
        while self.continue_hotel_flag:
            self._scrape_review_page()
            self._increase_page()
        logging.info('Iterated all reviews pages for the hotel. Going to next hotel')
        return
    
    def _iterate_hotels(self):
        """ Get hotel from db, setup the first page, and start iterating through reviews pages. Update flag at the end """
        while True:
            try:
                self._get_hotel_from_db()
                if self.continue_flag == False:
                    break
                self._load_hotel_page()
                self._push_all_languages_button()
                self._iterate_reviews_pages()
                self._update_reviews_flag()
            except Exception as e:
                logging.error(e)
                logging.error('Error in hotel, skipping to next hotel')
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





"""
fare delete insert per i commenti. non posso fare un unico commit, per evitare perdite grosse di dati?
aggiornare il flag solo alla fine

"""



"""
https://www.tripadvisor.com/Hotel_Review-g187791-d647933-Reviews-Vatican_Vista-Rome_Lazio.html

Vado alla pagina dell'hotel ^
Clicco su TUTTE LE LINGUE

ciclo:
Scrapo la pagina
Clicco bottone avanti

Inserire qualche check per vedere se la pagina è finita (non c'è più il bottone, e il numero di review matcha a quelle che leggo nella pagina a meno di epsilon?)

Quando ho finito di scrapare aggiornare flag review_scraped a 1 nel db

"""