import logging
import time
import sqlite3
import hashlib
import requests
import json
from keys import mapquest_key
from hotel_geocoder_exceptions import exception_dict


logging.basicConfig(filename='logs/hotel_geocoder.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

mapquest_endpoint = 'https://www.mapquestapi.com/geocoding/v1/address?key={}&inFormat=kvp&outFormat=json&location={}&thumbMaps=false'


class HotelGeocoder:
    def __init__(self):
        logging.info('Object instantiated')
        self.continue_flag = True
        self.hotel_id = None
        self.hotel_address = None
        self.rank = None
        self.location = {}
        self.mapquest_response_dict = {}
        self.locations_list = []

    @staticmethod
    def _get_hashed_id(string):
        # Calculate the SHA-256 hash of the string
        hash_value = hashlib.sha256(string.encode()).hexdigest()
        # Convert the hexadecimal hash value to an integer
        hash_int = int(hash_value, 16)
        # Truncate the integer to 20 digits. It has sufficient collision resistance for this use case
        truncated_hash = hash_int % (10 ** 18)
        return truncated_hash
    
    def _get_cursor(self):
        """ Get cursor to db """
        self.connection = sqlite3.connect('hotel.db', timeout=30) # increase timeout to run concurrently to scraping
        self.cursor = self.connection.cursor()
        logging.info('Got cursor')
        return
    
    def _get_hotel_from_db(self):
        """ Get hotel from db """
        # get hotel that has not been geocoded
        self.cursor.execute('select id from result where hotel_geocoded_flag=0 and hotel_scraped_flag=1 order by random() limit 1;')
        self.hotel_id = self.cursor.fetchone()[0] if self.cursor.fetchone() is not None else None
        if self.hotel_id is None:
            self.continue_flag = False
            logging.info('No more hotels to geocode')
            return
        else:
            # get hotel address from hotel table
            self.cursor.execute(f'select address from hotel where id={self.hotel_id};')
            self.hotel_address = self.cursor.fetchone()[0]
            logging.info(f'Got hotel from db')
            logging.info(f'Hotel id: {self.hotel_id}')
            logging.info(f'Hotel address: {self.hotel_address}')
            if self.hotel_id in exception_dict:
                self.hotel_address = exception_dict[self.hotel_id]
                logging.info(f'Found hotel in exception_dict')
                logging.info(f'New hotel address: {self.hotel_address}')
            return

    def _update_hotel_geocoded_flag(self):
        """ Update hotel geocoded flag in db """
        self.cursor.execute(f'update result set hotel_geocoded_flag=1 where id={self.hotel_id}')
        self.connection.commit()
        logging.info('Updated hotel geocoded flag')
        return

    def _get_mapquest_response(self):
        """ Geocode hotel """
        i = 0
        url = mapquest_endpoint.format(mapquest_key, self.hotel_address)
        while i < 3:
            try:
                mapquest_response = requests.get(url, timeout=30)
                mapquest_response.raise_for_status()
                self.mapquest_response_dict = mapquest_response.json()
                break
            except requests.exceptions.HTTPError as http_err:
                logging.error(http_err)
                logging.error('Non 200 response from API call')
                logging.exception('An error occurred')
                i += 1
                continue
            except Exception as e:
                logging.error(e)
                logging.error('Error in API call')
                logging.exception('An error occurred')
                i += 1
                continue
        logging.info('Got mapquest response, parsed and stored it in a dict')
        logging.info(self.mapquest_response_dict)
        return
    
    def _get_locations_list(self):
        """ Get locations list from mapquest response """
        self.locations_list = self.mapquest_response_dict['results'][0]['locations']
        logging.info('Got locations list')
        return
    
    def _iterate_locations(self):
        """ Iterate locations list """
        for self.rank, self.location in enumerate(self.locations_list):
            self._insert_replace_location()
        logging.info('Iterated all locations')
        return
        
    def _insert_replace_location(self):
        """ Insert location in db """
        self.cursor.execute(f"""
            insert or replace into HOTEL_MAPQUEST_LOCATION (
                id, hotel_id, rank, street, admin_area_6, admin_area_6_type, admin_area_5, admin_area_5_type, 
                admin_area_4, admin_area_4_type, admin_area_3, admin_area_3_type, admin_area_1, admin_area_1_type, 
                postal_code, geocode_quality_code, geocode_quality, drag_point, side_of_street, link_id, 
                unknown_input, type, latitude, longitude, display_latitude, display_longitude, map_url
            ) values (
                {self._get_hashed_id(str(self.hotel_id) + str(self.rank))}, 
                {self.hotel_id}, 
                {self.rank}, 
                "{self.location['street']}", 
                "{self.location['adminArea6']}", 
                "{self.location['adminArea6Type']}", 
                "{self.location['adminArea5']}", 
                "{self.location['adminArea5Type']}", 
                "{self.location['adminArea4']}", 
                "{self.location['adminArea4Type']}", 
                "{self.location['adminArea3']}", 
                "{self.location['adminArea3Type']}", 
                "{self.location['adminArea1']}", 
                "{self.location['adminArea1Type']}", 
                "{self.location['postalCode']}", 
                "{self.location['geocodeQualityCode']}", 
                "{self.location['geocodeQuality']}", 
                {self.location['dragPoint']}, 
                "{self.location['sideOfStreet']}", 
                "{self.location['linkId']}", 
                "{self.location['unknownInput']}", 
                "{self.location['type']}", 
                {self.location['latLng']['lat']}, 
                {self.location['latLng']['lng']}, 
                {self.location['displayLatLng']['lat']}, 
                {self.location['displayLatLng']['lng']}, 
                "{self.location['mapUrl']}"
            );
        """)
        self.connection.commit()
        logging.info('Inserted location')
        return

    def _insert_replace_mapquest_response(self):
        """ Insert or replace mapquest response in db, to store the raw response in case we need to debug """
        self.cursor.execute(f"""insert or replace into HOTEL_MAPQUEST_RESPONSE (hotel_id, response_raw) values ({self.hotel_id}, '{json.dumps(self.mapquest_response_dict).replace("'", "''")}');""")
        self.connection.commit()
        logging.info('Inserted or replaced mapquest response')
        return
    
    def _iterate_hotels(self):
        """ Iterate hotels """
        while True:
            self._get_hotel_from_db()
            if self.continue_flag == False:
                break
            self._get_mapquest_response()
            self._get_locations_list()
            self._iterate_locations()
            self._insert_replace_mapquest_response()
            self._update_hotel_geocoded_flag()
            time.sleep(0.3)
            logging.info('Done hotel, going to the next one')
        return


    def run(self):
        """ Run the instance of the class """
        try:
            self._get_cursor()
            self._iterate_hotels()
        except Exception as e:
            logging.error(e)
            logging.error('Error in run')
            logging.exception('An error occurred')
            raise e
        finally:
            logging.info('Quitting')
            self.connection.close()
        return

if __name__ == '__main__':
    hg = HotelGeocoder()
    hg.run()