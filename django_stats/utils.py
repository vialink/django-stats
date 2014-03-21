# coding: utf-8

import bisect

class TimeSeries(object):
    def __init__(self, history=False):
        # Maximum value.
        self.max = None

        # Minimum value.
        self.min = None

        # Sum of all values.
        self.sum = 0

        # Sum of all values squared.
        self.sum2 = 0

        # Number of records.
        self.qty = 0

        # History of all values.
        self.history = history
        self.values = []
    
    @property
    def average(self):
        return (1.0 * self.sum) / self.qty

    @property
    def variance(self):
        mu = self.average
        mu2 = (1.0 * self.sum2) / self.qty
        return mu2 - mu*mu

    @property
    def stddev(self):
        return self.variance ** 0.5

    def add(self, value):
        self.max = max(self.max, value) if self.max else value
        self.min = min(self.min, value) if self.min else value
        self.sum += value
        self.sum2 += value*value
        self.qty += 1
        if self.history:
            bisect.insort(self.values, value)

    def percentile(self, p):
        """ p must be between 0 and 1.
        """
        if not self.history:
            raise Exception('History is disabled.')
        idx = int(self.qty * p)
        return self.values[idx]

    def __unicode__(self):
        return u'interval=[{0}, {1}] average={2} stddev={3} quantity={4}'.format(self.min, self.max, self.average, self.stddev, self.qty)

