# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.urlresolvers import resolve, Resolver404

from urlparse import urlparse
import datetime
import bisect
import re

class LogLine(object):
    raw_fmt = '$remote_addr - $remote_user [$time_local]  "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $request_time'
    parsers = {
        'body_bytes_sent': int,
        'http_referer': str,
        'http_user_agent': str,
        'remote_addr': str,
        'remote_user': str,
        'request': str,
        'request_time': float,
        'status': int,
        'time_local': lambda x: datetime.datetime.strptime(x, '%d/%b/%Y:%H:%M:%S +0000'),
    }

    def __init__(self, line):
        self.raw = line
        self.compile_re()
        self.parse()

    def __unicode__(self):
        return u'{0} {1} {2} {3}'.format(self.method, self.status, self.request_time, self.raw_url)

    def compile_re(self):
        x = self.raw_fmt
        x2 = x.replace('[', '\[').replace(']', '\]')
        x3 = re.sub(r'\$(\w+)', '(?P<\\1>.*)', x2)
        x4 = '^{0}$'.format(x3)
        self.fmt = re.compile(x4)

    def parse(self):
        x = self.fmt.match(self.raw)
        if x is None:
            raise ValueError('Invalid line format.')

        # Set as attributes of the object.
        for k, v in x.groupdict().items():
            fn = self.parsers[k]
            setattr(self, k, fn(v))

        # Run other parsers.
        self.parse_other_fields()

    def parse_other_fields(self):
        self.method, x = self.request.split(' ', 1)
        self.raw_url, self.http = x.rsplit(' ', 1)
        self.url = urlparse(self.raw_url)

        try:
            self.view = resolve(unicode(self.url.path))
        except Resolver404:
            self.view = None

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

def parselog(filename):
    fp = file(filename, 'r')
    p1 = RequestByViewProcessor()
    for raw in fp:
        line = LogLine(raw.strip())
        p1.addline(line)
    fp.close()
    p1.to_str()

class Command(BaseCommand):
    args = u'<log>'
    help = u'Gera estatísticas de acesso aos webservices processando um arquivo de log do nginx'

    def handle(self, log, *args, **kwargs):
        parselog(log)
