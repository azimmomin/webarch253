"""
See sorted_title_words.out for answers.
"""

from mrjob.job import MRJob
from combine_user_visits import csv_readline

class TopPages(MRJob):

    def mapper(self, line_no, line):
        """Extracts the Vroot that was visited"""
        cell = csv_readline(line)
        if cell[0] == 'V':
            yield cell[1], 1
                  # What  Key, Value  do we want to output?

    def reducer(self, vroot, visit_counts):
        """Sumarizes the visit counts by adding them together.  If total visits
        is more than 400, yield the results"""
        total = sum(visit_counts)
                # How do we calculate the total visits from the visit_counts?
        yield vroot, total
                  # What  Key, Value  do we want to output?
        
if __name__ == '__main__':
    TopPages.run()
