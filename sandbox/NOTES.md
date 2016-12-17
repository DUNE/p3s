
# DEVELOPMENT NOTES
## Django Development Server
It is multithreaded by default, which all but
guarantees you will run into a race condition
if you don't somehow lock the database (which
is sqlite by default so unclear whether it's
possible. Option to turn threading off:
`
--nothreading
`

In addition, there is a way to ensure atomicity by
transaction-like behavior of requests, see 
https://docs.djangoproject.com/en/1.10/topics/db/transactions/

## Pilots view:
### Serialization
#### Using Django serializers
`    data = serializers.serialize('json', [ p, ])
     return HttpResponse(data)
`
### Sorting
#### Direct, by column
`
top_jobs = job.objects.order_by('-priority')
j = top_jobs[0]
`
#### Getting the distinct values:
`
jp = job.objects.values('priority').distinct()
pl =  []
for item in jp:
     val = item['priority']
     print(val)
     pl.append(val)
     pl.sort(reverse=True) # to get descending order
`
## Using the Django settings file to configure app settings
`
settings.MY_EXAMPLE_SETTING
`
## Time
### Finding a date/time in the past, by offset
`
t - timedelta(minutes=60)
`
Local time using Django timezine:
`
timezone.localtime(value).strftime("%Y%m%d%H%M")
`

Note that Django timezone will complain if you use
pytz to adjust datetime (which Django is trying to make
TZ-aware by itself).
