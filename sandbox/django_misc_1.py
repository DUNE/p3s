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
