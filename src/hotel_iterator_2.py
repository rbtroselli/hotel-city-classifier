import logging
from  base_iterator import BaseIterator
from geopy.geocoders import Nominatim


class HotelIterator(BaseIterator):
    """ Iterator to scrape hotel pages """

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # pass all arguments to parent class
        self.hotel_id = None
        self.hotel_url = None
        # attributes that go in the db
        self.hotel_dict = {
            'id': None,
            'url': None,
            'name': None,
            'address': None,
            'latitude': None,
            'longitude': None,
            'altitude': None,
            'description': None,
            'rating': None,
            'reviews': None,
            'category_rank': None,
            'star_rating': None,
            'nearby_restaurants': None,
            'nearby_attractions': None,
            'walkers_score': None,
            'pictures': None,
            'average_night_price': None,
            'price_range_min': None,
            'price_range_max': None,
            'property_amenities': None,
            'room_features': None,
            'room_types': None,
            'location_rating': None,
            'cleanliness_rating': None,
            'service_rating': None,
            'value_rating': None,
            'also_known_as': None,
            'formerly_known_as': None,
            'city_location': None,
            'number_of_rooms': None,
            'reviews_summary': None,
            'reviews_keypoint_location': None,
            'reviews_keypoint_atmosphere': None,
            'reviews_keypoint_rooms': None,
            'reviews_keypoint_value': None,
            'reviews_keypoint_cleanliness': None,
            'reviews_keypoint_service': None,
            'reviews_keypoint_amenities': None,
            'reviews_5_excellent': None,
            'reviews_4_very_good': None,
            'reviews_3_average': None,
            'reviews_2_poor': None,
            'reviews_1_terrible': None,
            'reviews_keywords': None
        }
        # additional attributes, to be flattened in the db
        self.hotel_amenities_dict = {}
        self.hotel_qualities_dict = {}
        self.hotel_additional_info_dict = {}
        self.hotel_reviews_keypoints_dict = {}
        self.hotel_reviews_distribution_dict = {}
        self.hotel_reviews_keywords_list = []
        # geocoding api attributes
        self.hotel_latitude = None
        self.hotel_longitude = None
        self.hotel_altitude = None
        logging.info('Completed subclass initialization')
        return

    

    # geocoding api call

    def _geocode_hotel(self): 
        """ Geocode hotel address to coordinates """
        geolocator = Nominatim(user_agent='hotel_locator_geocoder', timeout=30)
        location = geolocator.geocode(self.hotel_address)
        self.hotel_latitude = location.latitude if location is not None else None
        self.hotel_longitude = location.longitude if location is not None else None
        self.hotel_altitude = location.altitude if location is not None else None
        logging.info(f'Geocoded hotel: {self.hotel_latitude}, {self.hotel_longitude}, {self.hotel_altitude}')
        return
    


    # actual scraping 

    def _scrape_hotel_page(self):
        """ Scrape hotel data """
        self._reset_dict(self.hotel_dict) # reset dict before scraping
        self.hotel_dict['name'] = self.driver.find_element('class name', 'WMndO.f').text
        self.hotel_dict['address'] = self.driver.find_element('class name', 'FhOgt.H3.f.u.fRLPH').text
        self.hotel_dict['rating'] = self.driver.find_element('class name', 'kJyXc.P').text
        self.hotel_dict['reviews'] = self.driver.find_elements('class name', 'biGQs._P.pZUbB.KxBGd')[0].text.split(' ')[0].replace(',','')
        self.hotel_dict['category_rank'] = self.driver.find_elements('class name', 'biGQs._P.pZUbB.KxBGd')[1].text.replace('#', '').replace(',','')
        self.hotel_dict['star_rating'] = self.driver.find_element('class name', 'JXZuC.d.H0').get_attribute('textContent').split(' ')[0] if self.driver.find_elements('class name', 'JXZuC.d.H0') != [] else None
        self.hotel_dict['nearby_restaurants'] = self.driver.find_elements('class name', 'CllfH')[1].text.split(' ')[0].replace(',','')
        self.hotel_dict['nearby_attractions'] = self.driver.find_elements('class name', 'CllfH')[2].text.split(' ')[0].replace(',','')
        self.hotel_dict['walkers_score'] = self.driver.find_element('class name', 'UQxjK.H-').text if self.driver.find_elements('class name', 'UQxjK.H-') != [] else None
        self.hotel_dict['pictures'] = self.driver.find_element('class name', 'GuzzA').text.split('(')[-1].replace(')','').replace(',','') if self.driver.find_elements('class name', 'GuzzA') != [] else 0
        self.hotel_dict['average_night_price'] = self.driver.find_element('class name', 'biGQs._P.pZUbB.fOtGX').text.split('$')[-1].split(' ')[0].replace(',','') if self.driver.find_elements('class name', 'biGQs._P.pZUbB.fOtGX') != [] else None
        self.hotel_dict['reviews_summary'] = self.driver.find_element('class name', 'biGQs._P.pZUbB.ncFvv.KxBGd').text if self.driver.find_elements('class name', 'biGQs._P.pZUbB.ncFvv.KxBGd') != [] else 'No reviews summary'
        # hotel description
        if self.driver.find_elements('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB.bmUTE') != []: # desc with "Read more" button
            self.hotel_dict['description'] = self.driver.find_element('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB.bmUTE').find_element('class name', 'fIrGe._T').text
        elif self.driver.find_elements('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB') != []: # desc without "Read more" button
            self.hotel_dict['description'] = self.driver.find_element('class name', '_T.FKffI.TPznB.Ci.ajMTa.Ps.Z.BB').text
        else:
            self.hotel_dict['description'] = 'No description'
        # amenities
        amenities_titles_list = [] # get amenities titles
        for amenity_title in self.driver.find_elements('class name', 'vqEpQ.S5.b.Pf.ME'):
            amenity_title_text = amenity_title.text
            amenities_titles_list.append(amenity_title_text)
        amenities_box_list = [] # get amenities list, corresponding to each title
        for amenities_box in self.driver.find_elements('class name', 'Jevoh.K'):
            amenities_list = []
            for amenity in amenities_box.find_elements('class name', 'gFttI.f.ME.Ci.H3._c'):
                amenity_text = amenity.get_attribute('textContent')
                amenities_list.append(amenity_text)
            amenities_box_list.append(amenities_list)
        for i in range(len(amenities_titles_list)): # make a dict coupling previous 2 lists
            if i < len(amenities_box_list):
                self.hotel_amenities_dict[amenities_titles_list[i]] = amenities_box_list[i] 
        self.hotel_dict['property_amenities'] = ','.join(self.hotel_amenities_dict['Property amenities']) if 'Property amenities' in self.hotel_amenities_dict else 'NA'
        self.hotel_dict['room_features'] = ','.join(self.hotel_amenities_dict['Room features']) if 'Room features' in self.hotel_amenities_dict else 'NA'
        self.hotel_dict['room_types'] = ','.join(self.hotel_amenities_dict['Room types']) if 'Room types' in self.hotel_amenities_dict else 'NA'
        # hotel qualities: Location, Cleanliness, Service, Value
        for quality in self.driver.find_elements('class name', 'RZjkd'):
            quality_name = quality.find_element('class name', 'o').text
            logging.debug(f'Got quality: {quality_name}')
            quality_rating = quality.find_element('class name', 'biGQs._P.fiohW.biKBZ.osNWb').text
            logging.debug(f'Got quality rating: {quality_rating}')
            self.hotel_qualities_dict[quality_name] = quality_rating
        self.hotel_dict['location_rating'] = self.hotel_qualities_dict['Location'] if 'Location' in self.hotel_qualities_dict else -1
        self.hotel_dict['cleanliness_rating'] = self.hotel_qualities_dict['Cleanliness'] if 'Cleanliness' in self.hotel_qualities_dict else -1
        self.hotel_dict['service_rating'] = self.hotel_qualities_dict['Service'] if 'Service' in self.hotel_qualities_dict else -1
        self.hotel_dict['value_rating'] = self.hotel_qualities_dict['Value'] if 'Value' in self.hotel_qualities_dict else -1
        # additional info 
        additional_info_titles_list = [] # additional info titles
        for additional_info_title in self.driver.find_elements('class name', 'mpDVe.Ci.b'):
            additional_info_title_text = additional_info_title.text
            additional_info_titles_list.append(additional_info_title_text)
        additional_info_list = [] # additional info
        for additional_info in self.driver.find_elements('class name', 'IhqAp.Ci'):
            additional_info_text = additional_info.get_attribute('textContent')
            additional_info_list.append(additional_info_text)
        for i in range(len(additional_info_titles_list)): # make a dict coupling previous 2 lists
            self.hotel_additional_info_dict[additional_info_titles_list[i]] = additional_info_list[i]
        if 'PRICE RANGE' in self.hotel_additional_info_dict: # price range extremes
            self.hotel_additional_info_dict['PRICE RANGE'] = self.hotel_additional_info_dict['PRICE RANGE'].replace(' (Based on Average Rates for a Standard Room) ','')
            self.price_range_min = self.hotel_additional_info_dict['PRICE RANGE'].split(' - ')[0].replace('$','').replace(',','')
            self.price_range_max = self.hotel_additional_info_dict['PRICE RANGE'].split(' - ')[1].replace('$','').replace(',','')
            del self.hotel_additional_info_dict['PRICE RANGE']
        self.hotel_dict['also_known_as'] = self.hotel_additional_info_dict['ALSO KNOWN AS'] if 'ALSO KNOWN AS' in self.hotel_additional_info_dict else 'NA'
        self.hotel_dict['formerly_known_as'] = self.hotel_additional_info_dict['FORMERLY KNOWN AS'] if 'FORMERLY KNOWN AS' in self.hotel_additional_info_dict else 'NA'
        self.hotel_dict['city_location'] = self.hotel_additional_info_dict['LOCATION'] if 'LOCATION' in self.hotel_additional_info_dict else 'NA'
        self.hotel_dict['number_of_rooms'] = self.hotel_additional_info_dict['NUMBER OF ROOMS'] if 'NUMBER OF ROOMS' in self.hotel_additional_info_dict else -1
        self.hotel_dict['price_range_min'] = self.price_range_min if self.price_range_min is not None else -1
        self.hotel_dict['price_range_max'] = self.price_range_max if self.price_range_max is not None else -1
        # hotel reviews keypoints
        key_points = self.driver.find_elements('class name', 'zQDwR.f.Pe.PX.Pr.PJ.u._S.hJoAg')
        if key_points == []:
            return
        for point in key_points:
            point_name = point.find_element('class name', 'biGQs._P.pZUbB.qWPrE.hmDzD').text
            point_grade = point.find_element('class name', 'biGQs._P.kdCdj.ncFvv.fOtGX').text
            self.hotel_reviews_keypoints_dict[point_name] = point_grade
        self.hotel_dict['reviews_keypoint_location'] = self.hotel_reviews_keypoints_dict['Location'] if 'Location' in self.hotel_reviews_keypoints_dict else 'NA'
        self.hotel_dict['reviews_keypoint_atmosphere'] = self.hotel_reviews_keypoints_dict['Atmosphere'] if 'Atmosphere' in self.hotel_reviews_keypoints_dict else 'NA'
        self.hotel_dict['reviews_keypoint_rooms'] = self.hotel_reviews_keypoints_dict['Rooms'] if 'Rooms' in self.hotel_reviews_keypoints_dict else 'NA'
        self.hotel_dict['reviews_keypoint_value'] = self.hotel_reviews_keypoints_dict['Value'] if 'Value' in self.hotel_reviews_keypoints_dict else 'NA'
        self.hotel_dict['reviews_keypoint_cleanliness'] = self.hotel_reviews_keypoints_dict['Cleanliness'] if 'Cleanliness' in self.hotel_reviews_keypoints_dict else 'NA'
        self.hotel_dict['reviews_keypoint_service'] = self.hotel_reviews_keypoints_dict['Service'] if 'Service' in self.hotel_reviews_keypoints_dict else 'NA'
        self.hotel_dict['reviews_keypoint_amenities'] = self.hotel_reviews_keypoints_dict['Amenities'] if 'Amenities' in self.hotel_reviews_keypoints_dict else 'NA'
        # reviews keywords 
        keywords = self.driver.find_elements('class name', 'OKHdJ.z.Pc.PQ.Pp.PD.W._S.Gn.Rd._M.qWPrE.biKBZ.PQFNM.wSSLS')
        if keywords == []:
            logging.info('No reviews keywords found')
            return
        for keyword in keywords:
            self.hotel_reviews_keywords_list.append(keyword.text)
        self.hotel_reviews_keywords_list.remove('All reviews') # remove 'All reviews' from list
        self.hotel_dict['reviews_keywords'] = ','.join([keyword for keyword in self.hotel_reviews_keywords_list]) if self.hotel_reviews_keywords_list != [] else 'NA'
        # reviews distribution
        reviews_amounts = self.driver.find_elements('class name', 'QErCz')
        for i, review_amount in enumerate(reviews_amounts):
            self.hotel_reviews_distribution_dict[5-i] = review_amount.text.replace(',','')
        self.hotel_dict['reviews_5_excellent'] = self.hotel_reviews_distribution_dict[5]
        self.hotel_dict['reviews_4_very_good'] = self.hotel_reviews_distribution_dict[4]
        self.hotel_dict['reviews_3_average'] = self.hotel_reviews_distribution_dict[3]
        self.hotel_dict['reviews_2_poor'] = self.hotel_reviews_distribution_dict[2]
        self.hotel_dict['reviews_1_terrible'] = self.hotel_reviews_distribution_dict[1]
        # geocode hotel
        self._geocode_hotel()
        self.hotel_dict['latitude'] = self.hotel_latitude
        self.hotel_dict['longitude'] = self.hotel_longitude
        self.hotel_dict['altitude'] = self.hotel_altitude
        self.hotel_dict['id'] = self.hotel_id
        self.hotel_dict['url'] = self.hotel_url
        logging.info('Scraped hotel')
        for key, value in self.hotel_dict.items():
            if key in ('description', 'property_amenities', 'room_features', 'room_types', 'reviews_keywords', 'reviews_summary'):
                value_str = str(value)[:50] + ' [...] ' + str(value)[-50:] # Truncate string in log
            else:
                value_str = value
            logging.info(f'{key}: {value_str}')
        return
    
    
    
    # page setup (get page, check page)

    def _setup_page(self):
        """ Get page and check it. Retries implemented """
        self.url = self.hotel_url
        retries = 0
        while retries < 5:
            try:
                self._get_page()
                self._focus_browser_window()    
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
    
    def _focus_browser_window(self):
        """ Focus browser window to get all data loaded. Pricing does not load othewise """
        self.driver.switch_to.window(self.driver.window_handles[0])
        logging.info('Focused browser window')
        return
    
    

    # run method (hotel pages iteration)

    def _subclass_run(self):
        """ Iterate over hotels """
        while True:
            try:
                self.hotel_id, self.hotel_url = self._get_row_from_db(table='RESULT', column_list=['id', 'url'], condition='reviews>0 and hotel_scraped_flag=0')
                if (self.hotel_id == None and self.hotel_url == None): # no more hotels to scrape
                    logging.info('No more hotels to scrape')
                    break
                self._setup_page()
                self._scrape_hotel_page()
                self._insert_replace_row(table='HOTEL', column_value_dict=self.hotel_dict)
                self._update_flag(table='RESULT', column='hotel_scraped_flag', value=1, condition=f'id={self.hotel_id}')
                logging.info('Finished hotel')
                logging.info('-'*50)
            except Exception as e:
                logging.error('Error in iterating hotel, skipping hotel')
                logging.exception('An error occurred')
                continue
        logging.info('Finished iterating hotels')
        return
