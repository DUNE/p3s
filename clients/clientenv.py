#!/usr/bin/env python3.5
import os
#########################################################
def clientenv():

    (user, server, verb, site) = ('', 'http://localhost:8000/',  0, 'default')
        
    e = os.environ.keys()
    
    if 'USER' in e:
        user = os.environ['USER']
    else:
        print('EXITING: could not determine the user')
        exit(7)
        
    if 'P3S_SERVER' in e:	server	= os.environ['P3S_SERVER']
    if 'P3S_VERBOSITY' in e:	verb	= os.environ['P3S_VERBOSITY']
    if 'P3S_SITE' in e:		site	= os.environ['P3S_SITE']

    return (user, server, verb, site)

