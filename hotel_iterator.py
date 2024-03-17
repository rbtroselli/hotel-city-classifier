import logging
import time
import random
import sqlite3
from selenium import webdriver
from geopy.geocoders import Nominatim


logging.basicConfig(filename='logs/hotel_iterator.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

class HotelIterator:
    def __init__(self):
        logging.info('Object instantiated')
        self.driver = None
        self.connection = None
        self.cursor = None
        self.continue_flag = True
        # hotel attributes
        self.hotel_id = None
        self.hotel_url = None
        self.hotel_name = None
        self.hotel_address = None
        self.hotel_latitude = None
        self.hotel_longitude = None
        self.hotel_altitude = None
        self.hotel_description = None
        self.hotel_rating = None
        self.hotel_reviews = None
        self.hotel_category_rank = None
        self.hotel_star_rating = None
        self.hotel_nearby_restaurants = None
        self.hotel_nearby_attractions = None
        self.hotel_walkers_score = None
        self.hotel_pictures = None
        self.hotel_average_night_price = None
        self.price_range_min = None
        self.price_range_max = None
        self.hotel_amenities_dict = {}
        self.hotel_qualities = {}
        self.hotel_additional_info_dict = {}
        # review attributes
        self.hotel_reviews_summary = None
        self.hotel_reviews_keypoints = {}
        self.hotel_reviews_distribution = {}
        self.hotel_reviews_keywords = []
        return
    
    @staticmethod
    def _wait_humanly():
        """ Wait a random time between 5 and 15 seconds """
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
    
    
    def _update_scraped_flag(self):
        """ Update scraped flag in db """
        self.cursor.execute(f'update result set hotel_scraped_flag=1 where id={self.hotel_id}')
        logging.info('Updated scraped flag. Did not commit yet')
        return
    
    def _insert_data(self):
        """ Insert hotel data in db """
        query = (f"""
            insert into HOTEL (
                id, url, name, address, latitude, longitude, altitude, description, rating, reviews, category_rank, 
                star_rating, nearby_restaurants, nearby_attractions, walkers_score, pictures, average_night_price, 
                price_range_min, price_range_max, property_amenities, room_features, room_types, location_rating, 
                cleanliness_rating, service_rating, value_rating, also_known_as, formerly_known_as, city_location, 
                number_of_rooms, reviews_summary, reviews_keypoint_location, reviews_keypoint_atmosphere, reviews_keypoint_rooms,
                reviews_keypoint_value, reviews_keypoint_cleanliness, reviews_keypoint_service, reviews_keypoint_amenities, 
                reviews_5_excellent, reviews_4_very_good, reviews_3_average, reviews_2_poor, reviews_1_terrible, reviews_keywords
            )
            values (
                {self.hotel_id},
                '{self.hotel_url}',
                '{self.hotel_name.replace("'","''")}',
                '{self.hotel_address.replace("'","''")}',
                {self.hotel_latitude if self.hotel_latitude is not None else 999},
                {self.hotel_longitude if self.hotel_longitude is not None else 999},
                {self.hotel_altitude if self.hotel_altitude is not None else 999999},
                '{self.hotel_description.replace("'","''") if self.hotel_description != 'No description' else 'NA'}',
                {self.hotel_rating},
                {self.hotel_reviews},
                '{self.hotel_category_rank}',
                {self.hotel_star_rating if self.hotel_star_rating is not None else 0},
                {self.hotel_nearby_restaurants},
                {self.hotel_nearby_attractions},
                {self.hotel_walkers_score if self.hotel_walkers_score is not None else -1},
                {self.hotel_pictures},
                {self.hotel_average_night_price if self.hotel_average_night_price is not None else -1},
                {self.price_range_min if self.price_range_min is not None else -1},
                {self.price_range_max if self.price_range_max is not None else -1},
                '{','.join(self.hotel_amenities_dict['Property amenities']).replace("'","''") if 'Property amenities' in self.hotel_amenities_dict else 'NA'}',
                '{','.join(self.hotel_amenities_dict['Room features']).replace("'","''") if 'Room features' in self.hotel_amenities_dict else 'NA'}',
                '{','.join(self.hotel_amenities_dict['Room types']).replace("'","''") if 'Room types' in self.hotel_amenities_dict else 'NA'}',
                {self.hotel_qualities['Location'] if 'Location' in self.hotel_qualities else -1},
                {self.hotel_qualities['Cleanliness'] if 'Cleanliness' in self.hotel_qualities else -1},
                {self.hotel_qualities['Service'] if 'Service' in self.hotel_qualities else -1},
                {self.hotel_qualities['Value'] if 'Value' in self.hotel_qualities else -1},
                '{self.hotel_additional_info_dict['ALSO KNOWN AS'].replace("'","''") if 'ALSO KNOWN AS' in self.hotel_additional_info_dict else 'NA'}',
                '{self.hotel_additional_info_dict['FORMERLY KNOWN AS'].replace("'","''") if 'FORMERLY KNOWN AS' in self.hotel_additional_info_dict else 'NA'}',
                '{self.hotel_additional_info_dict['LOCATION'].replace("'","''") if 'LOCATION' in self.hotel_additional_info_dict else 'NA'}',
                {self.hotel_additional_info_dict['NUMBER OF ROOMS'] if 'NUMBER OF ROOMS' in self.hotel_additional_info_dict else -1},
                '{self.hotel_reviews_summary.replace("'","''") if self.hotel_reviews_summary != 'No reviews summary' else 'NA'}',
                '{self.hotel_reviews_keypoints['Location'] if 'Location' in self.hotel_reviews_keypoints else 'NA'}',
                '{self.hotel_reviews_keypoints['Atmosphere'] if 'Atmosphere' in self.hotel_reviews_keypoints else 'NA'}',
                '{self.hotel_reviews_keypoints['Rooms'] if 'Rooms' in self.hotel_reviews_keypoints else 'NA'}',
                '{self.hotel_reviews_keypoints['Value'] if 'Value' in self.hotel_reviews_keypoints else 'NA'}',
                '{self.hotel_reviews_keypoints['Cleanliness'] if 'Cleanliness' in self.hotel_reviews_keypoints else 'NA'}',
                '{self.hotel_reviews_keypoints['Service'] if 'Service' in self.hotel_reviews_keypoints else 'NA'}',
                '{self.hotel_reviews_keypoints['Amenities'] if 'Amenities' in self.hotel_reviews_keypoints else 'NA'}',
                {self.hotel_reviews_distribution[5]},
                {self.hotel_reviews_distribution[4]},
                {self.hotel_reviews_distribution[3]},
                {self.hotel_reviews_distribution[2]},
                {self.hotel_reviews_distribution[1]},
                '{','.join([keyword.replace("'","''") for keyword in self.hotel_reviews_keywords]) if self.hotel_reviews_keywords != [] else 'NA'}'
            );
        """)
        logging.debug(query)
        self.cursor.execute(query)  
        logging.info('Inserted data. Did not commit yet')
        return
    
    def _insert_update(self):
        """ Insert hotel data in databse. Update scraped_flag for the hotel id """
        self._insert_data()
        self._update_scraped_flag()
        self.connection.commit()
        logging.info('Committed insert and update')
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
                amenity_text = amenity.get_attribute('textContent')
                amenities_list.append(amenity_text)
            amenities_box_list.append(amenities_list)
        # make a dict coupling previous 2 lists
        for i in range(len(amenities_titles_list)):
            if i < len(amenities_box_list):
                self.hotel_amenities_dict[amenities_titles_list[i]] = amenities_box_list[i] 
        # log the first and last amenities for each key
        for key, value in self.hotel_amenities_dict.items():
            logging.info(f'Got {key}: {value[0]}, [...], {value[-1]}')
        return
    
    def _get_qualities(self):
        """ Get hotel qualities: Location, Cleanliness, Service, Value """
        for quality in self.driver.find_elements('class name', 'RZjkd'):
            quality_name = quality.find_element('class name', 'o').text
            logging.debug(f'Got quality: {quality_name}')
            quality_rating = quality.find_element('class name', 'biGQs._P.fiohW.biKBZ.osNWb').text
            logging.debug(f'Got quality rating: {quality_rating}')
            self.hotel_qualities[quality_name] = quality_rating
        # log qualities, key and value
        for key, value in self.hotel_qualities.items():
            logging.info(f'Got hotel quality: {key}: {value}')
        return
    
    def _get_description(self):
        """ Get hotel description """
        if self.driver.find_elements('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB.bmUTE') != []: # desc with "Read more" button
            self.hotel_description = self.driver.find_element('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB.bmUTE').find_element('class name', 'fIrGe._T').text
        elif self.driver.find_elements('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB') != []: # desc without "Read more" button
            self.hotel_description = self.driver.find_element('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB').text
        else:
            self.hotel_description = 'No description' # no description
        logging.info(f'Got hotel description: {self.hotel_description[:30]} [...], {self.hotel_description[-30:]}')
        return
    
    def _get_reviews_keypoints(self):
        """ Get hotel reviews keypoints """
        key_points = self.driver.find_elements('class name', 'zQDwR.f.Pe.PX.Pr.PJ.u._S.hJoAg')
        if key_points == []:
            return
        for point in key_points:
            point_name = point.find_element('class name', 'biGQs._P.pZUbB.qWPrE.hmDzD').text
            point_grade = point.find_element('class name', 'biGQs._P.kdCdj.ncFvv.fOtGX').text
            self.hotel_reviews_keypoints[point_name] = point_grade
        for key, value in self.hotel_reviews_keypoints.items():
            logging.info(f'Got keypoint: {key}: {value}')
        return
    
    def _get_reviews_keywords(self):
        """ Get comments keywords """
        keywords = self.driver.find_elements('class name', 'OKHdJ.z.Pc.PQ.Pp.PD.W._S.Gn.Rd._M.qWPrE.biKBZ.PQFNM.wSSLS')
        if keywords == []:
            logging.info('No reviews keywords found')
            return
        for keyword in keywords:
            self.hotel_reviews_keywords.append(keyword.text)
        self.hotel_reviews_keywords.remove('All reviews') # remove 'All reviews' from list
        logging.info(f'Got reviews keywords: {self.hotel_reviews_keywords[0]}, [...], {self.hotel_reviews_keywords[-1]}')
        return
    
    def _get_reviews_distribution(self):
        """ Get reviews distribution """
        reviews_amounts = self.driver.find_elements('class name', 'QErCz')
        for i, review_amount in enumerate(reviews_amounts):
            self.hotel_reviews_distribution[5-i] = review_amount.text.replace(',','')
        logging.info(f'Got reviews distribution: {self.hotel_reviews_distribution}')
        return
    
    def _get_additional_info(self):
        """ Get additional info from the bottom of the page """
        # get additional info titles
        additional_info_titles_list = [] 
        for additional_info_title in self.driver.find_elements('class name', 'mpDVe.Ci.b'):
            additional_info_title_text = additional_info_title.text
            additional_info_titles_list.append(additional_info_title_text)
        # get additional info, corresponding to each title
        additional_info_list = []
        for additional_info in self.driver.find_elements('class name', 'IhqAp.Ci'):
            additional_info_text = additional_info.get_attribute('textContent')
            additional_info_list.append(additional_info_text)
        # make a dict coupling previous 2 lists. Filter for only some additional info
        for i in range(len(additional_info_titles_list)):
            self.hotel_additional_info_dict[additional_info_titles_list[i]] = additional_info_list[i]
        # get price range extremes
        if 'PRICE RANGE' in self.hotel_additional_info_dict:
            self.hotel_additional_info_dict['PRICE RANGE'] = self.hotel_additional_info_dict['PRICE RANGE'].replace(' (Based on Average Rates for a Standard Room) ','')
            self.price_range_min = self.hotel_additional_info_dict['PRICE RANGE'].split(' - ')[0].replace('$','').replace(',','')
            self.price_range_max = self.hotel_additional_info_dict['PRICE RANGE'].split(' - ')[1].replace('$','').replace(',','')
            del self.hotel_additional_info_dict['PRICE RANGE']
        # print additional info
        for key, value in self.hotel_additional_info_dict.items():
            logging.info(f'Got {key}: {value}')
        logging.info(f'Got price range: {self.price_range_min} - {self.price_range_max}')
        return

    def _scrape_hotel(self):
        """ Scrape hotel data """
        self.hotel_name = self.driver.find_element('class name', 'WMndO.f').text
        self.hotel_address = self.driver.find_element('class name', 'FhOgt.H3.f.u.fRLPH').text
        self.hotel_rating = self.driver.find_element('class name', 'kJyXc.P').text
        self.hotel_reviews = self.driver.find_elements('class name', 'biGQs._P.pZUbB.KxBGd')[0].text.split(' ')[0].replace(',','')
        self.hotel_category_rank = self.driver.find_elements('class name', 'biGQs._P.pZUbB.KxBGd')[1].text.replace('#', '').replace(',','')
        self.hotel_star_rating = self.driver.find_element('class name', 'JXZuC.d.H0').get_attribute('textContent').split(' ')[0] if self.driver.find_elements('class name', 'JXZuC.d.H0') != [] else None
        self.hotel_nearby_restaurants = self.driver.find_elements('class name', 'CllfH')[1].text.split(' ')[0].replace(',','')
        self.hotel_nearby_attractions = self.driver.find_elements('class name', 'CllfH')[2].text.split(' ')[0].replace(',','')
        self.hotel_walkers_score = self.driver.find_element('class name', 'UQxjK.H-').text if self.driver.find_elements('class name', 'UQxjK.H-') != [] else None
        self.hotel_pictures = self.driver.find_element('class name', 'GuzzA').text.split('(')[-1].replace(')','').replace(',','')
        self.hotel_average_night_price = self.driver.find_element('class name', 'biGQs._P.pZUbB.fOtGX').text.split('$')[-1].split(' ')[0].replace(',','') if self.driver.find_elements('class name', 'biGQs._P.pZUbB.fOtGX') != [] else None
        self.hotel_reviews_summary = self.driver.find_element('class name', 'biGQs._P.pZUbB.ncFvv.KxBGd').text if self.driver.find_elements('class name', 'biGQs._P.pZUbB.ncFvv.KxBGd') != [] else 'No reviews summary'
        logging.info('Scraped hotel')
        logging.info(f'Name: {self.hotel_name}')
        logging.info(f'Address: {self.hotel_address}')
        logging.info(f'Hotel rating: {self.hotel_rating}')
        logging.info(f'Hotel reviews: {self.hotel_reviews}')
        logging.info(f'Hotel rank: {self.hotel_category_rank}')
        logging.info(f'Hotel star rating: {self.hotel_star_rating}')
        logging.info(f'Nearby restaurants: {self.hotel_nearby_restaurants}')
        logging.info(f'Nearby attractions: {self.hotel_nearby_attractions}')
        logging.info(f'Walkers grade: {self.hotel_walkers_score}')
        logging.info(f'Pictures: {self.hotel_pictures}')
        logging.info(f'Typical price: {self.hotel_average_night_price}')
        logging.info(f'Reviews summary: {self.hotel_reviews_summary[:30]} [...] {self.hotel_reviews_summary[-30:]}')
        self._geocode_hotel()
        self._get_description()
        self._get_amenities()
        self._get_qualities()
        self._get_additional_info()
        self._get_reviews_keypoints()
        self._get_reviews_keywords()
        self._get_reviews_distribution()
        return
    

    def _check_hotel_page(self):
        """ Check if hotel page is valid """
        if self.driver.find_elements('class name', 'WMndO.f') == []:
            raise Exception('No name found, invalid page')
        logging.info('Checked page')
        return
    
    def _focus_browser_window(self):
        """ Focus browser window to get all data loaded """
        self.driver.switch_to.window(self.driver.window_handles[0])
        logging.info('Focused browser window')
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
                self._focus_browser_window()    
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
    

    def _get_hotel_from_db(self):
        """ Get hotel from db """
        self.cursor.execute('select id, url from result where reviews>50 and hotel_scraped_flag=0 order by random() limit 1;')
        # self.cursor.execute('select id, url from result where id=414003738016358719 and hotel_scraped_flag=0 order by random() limit 1;')
        row = self.cursor.fetchone()
        if row is not None:
            self.hotel_id, self.hotel_url = row
            logging.info(f'Got hotel from db')
            logging.info(f'Hotel id: {self.hotel_id}')
            logging.info(f'Hotel url: {self.hotel_url}')
            return
        else:
            self.continue_flag = False
            logging.info('No more hotels to scrape')
            return
        
    def _reset_attributes(self):
        """ Reset attributes to None """
        self.hotel_id = None
        self.hotel_url = None
        self.hotel_name = None
        self.hotel_address = None
        self.hotel_latitude = None
        self.hotel_longitude = None
        self.hotel_altitude = None
        self.hotel_description = None
        self.hotel_rating = None
        self.hotel_reviews = None
        self.hotel_category_rank = None
        self.hotel_star_rating = None
        self.hotel_nearby_restaurants = None
        self.hotel_nearby_attractions = None
        self.hotel_walkers_score = None
        self.hotel_pictures = None
        self.hotel_average_night_price = None
        self.price_range_min = None
        self.price_range_max = None
        self.hotel_amenities_dict = {}
        self.hotel_qualities = {}
        self.hotel_additional_info_dict = {}
        self.hotel_reviews_summary = None
        self.hotel_reviews_keypoints = {}
        self.hotel_reviews_distribution = {}
        self.hotel_reviews_keywords = []
        logging.info('Reset attributes')
        return
        

    def _iterate_hotel(self):
        """ Iterate over hotel pages and scrape data """
        while True:
            try:
                self._get_hotel_from_db()
                if self.continue_flag == False:
                    break
                self._load_hotel_page()
                self._scrape_hotel()
                self._insert_update()
                self._reset_attributes()
                logging.info('Finished hotel')
                logging.info('-'*50)
            except Exception as e:
                self._reset_attributes()
                logging.error(e)
                logging.info('Error in hotel scraping or inserting data, skipping hotel')
                logging.info('-'*50)
                continue
        logging.info('Finished iterating hotels')
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
            self._wait_humanly()
            self.driver.quit()
            self.connection.close()
        return

if __name__ == '__main__':
    hi = HotelIterator()
    hi.run()
