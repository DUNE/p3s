#!/usr/bin/env python3
import subprocess
import time
p = subprocess.Popen(['sleep', '10'], shell=False)

err = None

while True:
    err = p.poll()
    if err is None:
        print('waiting')
    else:
        break
    time.sleep(1)

print(err)


