#!/usr/bin/python

import signal

def handler(signal, frame):
    print 'pressed ctrl+c'

signal.signal(signal.SIGINT, handler)
print 'press'
signal.pause()
