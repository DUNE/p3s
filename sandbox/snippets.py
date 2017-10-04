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

# Django response API
headers		= response.info()
data		= response.read()

response_url	= response.geturl()
response_date	= headers['date']

# Django tables
uuid = tables.LinkColumn(viewname='dummy',
                         args=[A('pk')], text='foo', orderable=False,
                         empty_values=())

def render_uuid(self,value):
    return mark_safe('<a href="http://%s%s?uuid=%s">%s</a>' % (self.site, reverse('pilots'), value, value))

def render_j_uuid(self,value):
    return mark_safe('<a href="http://%s%s?uuid=%s">%s</a>' % (self.site, reverse('jobs'), value, value))

def render_id(self,value):
    return mark_safe('<a href="http://%s%s?pk=%s">%s</a>' % (self.site, reverse('pilots'), value, value))
