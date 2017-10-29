import json

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
    if('.json' in json_in):
        try:
            with open(json_in) as data_file:    
                data = json.load(data_file)
        except:
            if(verb>0): print('Failed to parse JSON')
            exit(-3)
    else:
        data = json.loads(json_in)
    return data
###################################################################
