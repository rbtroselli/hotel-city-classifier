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
        return
    

    def _insert_data(self):
        """ Insert hotel data in db """
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
        geolocator = Nominatim(user_agent='hotel_locator_geocoder')
        location = geolocator.geocode(self.hotel_address)
        self.hotel_latitude = location.latitude if location is not None else None
        self.hotel_longitude = location.longitude if location is not None else None
        self.hotel_altitude = location.altitude if location is not None else None
        logging.info(f'Geocoded hotel: {self.hotel_latitude}, {self.hotel_longitude}, {self.hotel_altitude}')
        return

    def _scrape_hotel(self):
        """ Scrape hotel data """
        self.hotel_name = self.driver.find_element('class name', 'WMndO.f').text
        self.hotel_address = self.driver.find_element('class name', 'FhOgt.H3.f.u.fRLPH').text
        self.hotel_description = self.driver.find_element('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB').text
        
        
        
        
        
        self._geocode_hotel()
        self._get_amenities()
        return
    
    
    def _check_hotel_page(self):
        """ Check if hotel page is valid """
        if self.driver.find_elements('class name', 'WMndO.f') == []:
            raise Exception('No name found, invalid page')
        return
    
    def _get_hotel_page(self):
        """ Get hotel page """
        self.driver.get(self.hotel_url)
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
                logging.info('Hotel page loaded')
                break
            except Exception as e:
                retries += 1
                logging.error(e)
                logging.error(f'Page not loaded, retry {retries}')
                time.sleep(30)
                continue
        return
    

    def _get_hotel_from_db(self):
        """ Get hotel from db """
        self.cursor.execute('select id, url from result where reviews>1 and scraped_flag=0 order by random() limit 1;')
        # to do: put this code in its function, somehow:
        if self.cursor.fetchone() is not None:
            self.hotel_id = self.cursor.fetchone()[0]
            self.hotel_url = self.cursor.fetchone()[1]
            logging.info(f'Got hotel from db: {self.hotel_id}, {self.hotel_url}')
            return
        else:
            self.continue_flag = False
            logging.info('No more hotels to scrape')
            return
    

    def _iterate_hotel(self):
        """ Iterate over hotel pages and scrape data """
        while True:
            self._get_hotel_from_db()
            if self.continue_flag == False:
                break
            self._load_hotel_page()
            self._scrape_hotel()
            self._insert_data()
            self._update_scraped_flag()
        return

    def run(self):
        """ Run the search iterator """
        try:
            self._get_driver()
            self._get_cursor()
            self._iterate_hotel()
        finally:
            time.sleep(600)
            self.driver.quit()
            self.connection.close()
        return

if __name__ == '__main__':
    hi = HotelIterator()
    hi.run()