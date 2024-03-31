from base_iterator import BaseIterator
from result_iterator import ResultIterator
from review_iterator import ReviewIterator


if __name__ == '__main__':
    bi = ReviewIterator(test=True)
    bi.run()
