"""Find users with more than 20 visits.

This program will take a CSV data file and output tab-seperated lines of

    Vroot -> number of visits

To run:

    python top_users.py c-anonymous-msweb.data

To store output:

    python top_users.py c-anonymous-msweb.data > top_users.out
"""

from mrjob.job import MRJob
from combine_user_visits import csv_readline

class TopUserss(MRJob):

    def mapper(self, line_no, line):
        """Extracts the Vroot that was visited"""
        cell = csv_readline(line)
        if cell[0] == 'V':
            yield cell[3], 1
                  # What  Key, Value  do we want to output?

    def reducer(self, vroot, visit_counts):
        """Sumarizes the visit counts by adding them together.  If total visits
        is more than 400, yield the results"""
        total = sum(visit_counts)
                # How do we calculate the total visits from the visit_counts?
        if total > 20:
            yield vroot, total
                  # What  Key, Value  do we want to output?
        
if __name__ == '__main__':
    TopUsers.run()
