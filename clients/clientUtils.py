import json
from collections import OrderedDict
###################################################################
def logexit(mode, msg, logger):
    if(mode=='FAIL'):
        error = ''
        try:
            error	= msg['error'] # if the server told us what the error was, log it
            logger.error('exiting, received FAIL status from server, error:%s' % error)
        except:
            logger.error('exiting, received FAIL status from server, no error returned')

    else:
        logger.info('exiting, received KILL status from server')
            
    exit(0)
###################################################################
def takeJson(json_in, verb):
    data=None

    if('.json' in json_in):
        try:
            f=open(json_in)
            if(verb>0): print("Opened file:", json_in)
            data=json.load(f)		# , object_pairs_hook=OrderedDict)
        except:
            if(verb>0): print('Failed to open or parse JSON file:', json_in)
            exit(-3)
    else:
        data = json.loads(json_in)	# , object_pairs_hook=OrderedDict)
    return data
###################################################################
def parseCommaDash(inp):
    outlist = []
    if('-' in inp):
        left_right = inp.split('-')
        for x in range(int(left_right[0]), int(left_right[1])+1):
            outlist.append(str(x))
    elif(',' in inp):
        outlist=inp.split(',')
    else:
        outlist.append(inp)
        
    return ','.join(outlist)
