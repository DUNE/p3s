def handler(signum, frame):
    print('Here you go')

signal.signal(signal.SIGINT, handler)
