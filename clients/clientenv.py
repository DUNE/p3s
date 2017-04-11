#!/usr/bin/env python3.5
import os
#########################################################
def clientenv():
    user	= os.environ['USER']
    try:
        server	= os.environ['P3S_SERVER']
    except:
        server	= 'http://localhost:8000/'
    
    try:
        verb	= os.environ['P3S_VERBOSITY']
    except:
        verb	= 0

    return (user, server, verb)

