import json
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

