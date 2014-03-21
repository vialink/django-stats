# coding: utf-8

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

