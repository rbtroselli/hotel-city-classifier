from base_iterator import BaseIterator
from result_iterator import ResultIterator
from hotel_iterator import HotelIterator
from review_iterator import ReviewIterator


if __name__ == '__main__':
    bi = ReviewIterator(test=False, log_file_name='review_iterator.log', db_name='hotel.db', db_connection=True, browser_driver=True)
    bi.run()
