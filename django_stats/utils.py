# coding: utf-8

class TimeSeries(object):
    def __init__(self, history=False):
        self.max = None
        self.min = None
        self.sum = 0
        self.qty = 0
        self.values = []
        self.history = history
    
    @property
    def average(self):
        return (1.0 * self.sum) / self.qty

    def add(self, value):
        self.max = max(self.max, value) if self.max else value
        self.min = min(self.min, value) if self.min else value
        self.sum += value
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
        return u'interval=[{0}, {1}] average={2} quantity={3}'.format(self.min, self.max, self.average, self.qty)

