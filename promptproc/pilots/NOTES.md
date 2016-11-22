
# DEVELOPMENT NOTES
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