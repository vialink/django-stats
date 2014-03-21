# coding: utf-8

def parselog(filename):
    fp = file(filename, 'r')
    p1 = RequestByViewProcessor()
    for raw in fp:
        line = LogLine(raw.strip())
        p1.addline(line)
    fp.close()
    p1.to_str()
