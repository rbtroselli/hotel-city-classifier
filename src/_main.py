from base_iterator import BaseIterator
from result_iterator import ResultIterator
from hotel_iterator_2 import HotelIterator
from review_iterator import ReviewIterator


if __name__ == '__main__':
    bi = HotelIterator(test=True, log_file_name='hotel_iterator.log', db_name='test.db', db_connection=True, browser_driver=True)
    bi.run()
