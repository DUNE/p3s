import datetime
from datetime import datetime
from datetime import time
from datetime import timedelta


def dt(stringTime):
    seconds=0
    minutes=0
    hours=0
    days=0
    years=0
    
    elements = stringTime.split(':')

    try:
        seconds=int(elements[-1])
    except:
        pass
    
    try:
        minutes=int(elements[-2])
    except:
        pass
    
    try:
        hours=int(elements[-3])
    except:
        pass
    
    try:
        days=int(elements[-4])
    except:
        pass
    
    try:
        years=int(elements[-5])
    except:
        pass
    
    return timedelta(days=(days + years*365), hours=hours, minutes=minutes, seconds=seconds)


def uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds = uptime_seconds))

        return uptime_string

