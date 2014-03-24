# coding: utf-8

from .parsers import LogLine
from .processors import RequestByViewProcessor

def parselog(filename, since=None, slow_threshold=None):
    fp = file(filename, 'r')
    p1 = RequestByViewProcessor(since=since)
    for raw in fp:
        line = LogLine(raw.strip())
        p1.addline(line)
    fp.close()
    p1.to_str(slow_threshold=slow_threshold)
