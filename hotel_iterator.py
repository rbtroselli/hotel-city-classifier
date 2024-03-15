import logging
import time
import random
import undetected_chromedriver as uc
import sqlite3
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium import webdriver
from geopy.geocoders import Nominatim
from selenium.common.exceptions import NoSuchElementException


# logging.basicConfig(filename='logs/hotel_iterator.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

class HotelIterator:
    def __init__(self):
        logging.info('Object instantiated')
        self.driver = None
        self.connection = None
        self.cursor = None
        
        self.continue_flag = True
        self.hotel_id = None
        self.hotel_url = None
        self.hotel_name = None
        self.hotel_address = None
        self.hotel_description = None
        self.hotel_latitude = None
        self.hotel_longitude = None
        self.hotel_altitude = None
        self.hotel_amenities_dict = {}
        self.hotel_qualities = {}
        self.hotel_rating = None
        self.hotel_reviews = None

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
    
    
    def _update_scraped_flag(self):
        """ Update scraped flag in db """
        # self.cursor.execute(f'update result set scraped_flag=1 where id={self.hotel_id}')
        self.cursor.execute('select 1')
        self.connection.commit()

        # to do: un-comment correct update, when finished testing
        return
    

    def _insert_data(self):
        """ Insert hotel data in db """
        # to do: insert code
        # costruire la query in maniera ricorsiva, con i valori che non sono sempre presenti, tipo le amenities
        return
    

    def _get_amenities(self):
        """ Get hotel amenities """
        # get amenities titles
        amenities_titles_list = [] 
        for amenity_title in self.driver.find_elements('class name', 'vqEpQ.S5.b.Pf.ME'):
            amenity_title_text = amenity_title.text
            amenities_titles_list.append(amenity_title_text)
        # get amenities list, corresponding to each title
        amenities_box_list = []
        for amenities_box in self.driver.find_elements('class name', 'Jevoh.K'):
            amenities_list = []
            for amenity in amenities_box.find_elements('class name', 'gFttI.f.ME.Ci.H3._c'):
                amenity_text = amenity.get_attribute("textContent")
                amenities_list.append(amenity_text)
            amenities_box_list.append(amenities_list)
        # make a dict coupling previous 2 lists
        for i in range(len(amenities_titles_list)):
            if i < len(amenities_box_list):
                self.hotel_amenities_dict[amenities_titles_list[i]] = amenities_box_list[i] 
        logging.info(f'Got amenities: {self.hotel_amenities_dict}')
        return
    
    def _geocode_hotel(self): 
        """ Geocode hotel address to coordinates """
        geolocator = Nominatim(user_agent='hotel_locator_geocoder', timeout=30)
        location = geolocator.geocode(self.hotel_address)
        self.hotel_latitude = location.latitude if location is not None else None
        self.hotel_longitude = location.longitude if location is not None else None
        self.hotel_altitude = location.altitude if location is not None else None
        logging.info(f'Geocoded hotel: {self.hotel_latitude}, {self.hotel_longitude}, {self.hotel_altitude}')
        return
    
    def _get_hotel_qualities(self):
        """ Get hotel qualities: Location, Cleanliness, Service, Value """
        for quality in self.driver.find_elements('class name', 'RZjkd'):
            quality_name = quality.find_element('class name', 'o').text
            logging.info(f'Got quality: {quality_name}')
            quality_rating = quality.find_element('class name', 'biGQs._P.fiohW.biKBZ.osNWb').text
            logging.info(f'Got quality rating: {quality_rating}')
            self.hotel_qualities[quality_name] = quality_rating
        logging.info(f'Got hotel qualities: {self.hotel_qualities}')
        return

    def _scrape_hotel(self):
        """ Scrape hotel data """
        self.hotel_name = self.driver.find_element('class name', 'WMndO.f').text
        self.hotel_address = self.driver.find_element('class name', 'FhOgt.H3.f.u.fRLPH').text
        try:
            self.hotel_description = self.driver.find_element('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB').text
        except NoSuchElementException:
            self.hotel_description = 'No description'
        self.hotel_rating = self.driver.find_element('class name', 'kJyXc.P').text
        self.hotel_reviews = (
            self.driver
            .find_element('class name', 'UikNM._G.B-._S._W._T.c.G_.wSSLS.TXrCr.raEkE')
            .find_element('class name', 'biGQs._P.pZUbB.KxBGd')
            .text
            .split(' ')[0]
            .replace(',','')
        )

        logging.info('Scraped hotel')
        logging.info(f'Name: {self.hotel_name}')
        logging.info(f'Address: {self.hotel_address}')
        logging.info(f'Description: {self.hotel_description}')
        logging.info(f'Hotel rating: {self.hotel_rating}')
        logging.info(f'Hotel reviews: {self.hotel_reviews}')
        
        
        
        # to do: get all missing information from the page

        self._geocode_hotel()
        self._get_amenities()
        self._get_hotel_qualities()
        return
    
    
    def _check_hotel_page(self):
        """ Check if hotel page is valid """
        if self.driver.find_elements('class name', 'WMndO.f') == []:
            raise Exception('No name found, invalid page')
        logging.info('Checked page')
        return
    
    def _get_hotel_page(self):
        """ Get hotel page """
        # self.driver.get(self.hotel_url)
        # test: 
        self.driver.get('https://www.tripadvisor.com/Hotel_Review-g187791-d21203734-Reviews-Casavignoni-Rome_Lazio.html')
        logging.info('Got page')
        time.sleep(random.uniform(20, 40))
        return
    
    def _load_hotel_page(self):
        """ Get hotel page, and check if valid. Catch exceptions and retry up to 10 times """
        retries = 0
        while retries < 10:
            try:
                self._get_hotel_page()
                self._check_hotel_page()
                logging.info('Loaded hotel page')
                break
            except Exception as e:
                retries += 1
                logging.error(e)
                logging.error(f'Did not load hotel page, retry {retries}')
                time.sleep(5)
                continue
        return
    

    def _get_hotel_from_db(self):
        """ Get hotel from db """
        self.cursor.execute('select id, url from result where reviews>1 and hotel_scraped_flag=0 order by random() limit 1;')
        # to do: put this code in its function, somehow:
        row = self.cursor.fetchone()
        if row is not None:
            self.hotel_id, self.hotel_url = row
            logging.info(f'Got hotel from db: {self.hotel_id}, {self.hotel_url}')
            return
        else:
            self.continue_flag = False
            logging.info('No more hotels to scrape')
            return
        
    def _update_insert(self):
        """ Insert hotel data in databse. Update scraped_flag for the hotel id """
        self._insert_data()
        self.connection.commit()
        return
        self._update_scraped_flag()
        self.connection.commit()
        return
    

    def _iterate_hotel(self):
        """ Iterate over hotel pages and scrape data """
        while True:
            self._get_hotel_from_db()
            if self.continue_flag == False:
                break
            self._load_hotel_page()
            self._scrape_hotel()
            self._update_insert()

            break # testing
        logging.info('Finished iteration')
        return

    def run(self):
        """ Run the search iterator """
        try:
            self._get_driver()
            self._get_cursor()
            self._iterate_hotel()
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            logging.info('Quitting')
            # time.sleep(600)
            input('___')
            self.driver.quit()
            self.connection.close()
        return

if __name__ == '__main__':
    hi = HotelIterator()
    hi.run()

    # insert hotel e aggiornamento flag nello stesso commit, 
    # così se va in errore, o se stoppo il programma, il flag non è aggiornato in maniera errata