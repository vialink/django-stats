# coding: utf-8

from .utils import TimeSeries

class RequestByViewProcessor(object):
    def __init__(self):
        self.data = {}

    def addline(self, line):
        key = (line.view.url_name, line.method, line.status)
        ts = self.data.get(key, None)
        if ts is None:
            ts = TimeSeries(history=True)
            self.data[key] = ts
        ts.add(line.request_time)

    def to_str(self):
        a = self.data.items()
        a.sort(key=lambda x: x[0])
        for x in a:
            print x[0], unicode(x[1]), '50%:{0}'.format(x[1].percentile(0.5)), '90%:{0}'.format(x[1].percentile(0.9))

