#!/usr/bin/env python3

import os
import subprocess
import shlex
import time

os.environ['TESTVAR'] = 'TESTVAL'

cmd = 'env'

p = subprocess.Popen(shlex.split(cmd),
                     stdout=subprocess.PIPE,
                     shell=False)

err = None

while True:
    err = p.poll()
    if err is None:
        print('waiting')
    else:
        print(p.stdout.read().decode('utf-8'))
        break
    time.sleep(1)

print('TEST1 Exit code:', err)


cmd = 'python3 envlist.py'

p = subprocess.Popen(shlex.split(cmd),
                     stdout=subprocess.PIPE,
                     shell=False)

err = None

while True:
    err = p.poll()
    if err is None:
        print('waiting')
    else:
        print(p.stdout.read().decode('utf-8'))
        break
    time.sleep(1)

print('TEST2 Exit code:', err)


