#!/usr/bin/env python3.5
import signal, os
import time

def handler(signum, frame):
    print('Signal handler called with signal', signum)

signal.signal(signal.SIGTERM, handler)

while(True):
    time.sleep(5)
