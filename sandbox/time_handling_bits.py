# handling time and time difference etc
yest = datetime.datetime.now() - timedelta(days=1)
for o in objects.filter(ts_lhb__gte=yest):
    print(o.ts_lhb)
###############################################
t = datetime.strptime("0001:023:05:20:25","%Y:%j:%H:%M:%S")
