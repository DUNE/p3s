# This file is not meant to contain functioning code, it contains
# snippets removed from the p3s project which were added sometimes
# on experimental basis.

# Time Since File Creation
time.mktime(datetime.now().timetuple())-os.path.getctime("foo")

# signal handling
def handler(signum, frame):
    print('Here you go')

signal.signal(signal.SIGINT, handler)

# To get history in an interactive Python session
import readline
for i in range(readline.get_current_history_length()):
    print(readline.get_history_item(i + 1))
