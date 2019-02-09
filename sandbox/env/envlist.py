import os

for k in   os.environ.keys():
    print('%s=%s' % (k,os.environ[k]))
