
# DEVELOPMENT NOTES
## Pilots view:
### Serialization

`     data = serializers.serialize('json', [ p, ])
     return HttpResponse(data)
`
### Sorting
`top_jobs = job.objects.order_by('-priority')
j = top_jobs[0]
`
