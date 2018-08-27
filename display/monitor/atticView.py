#########################################################    
# THIS IS A COLLECTION OF CERTAIN OBSOLETED METHODS
# THAT USED TO BE IN THE MONITOR VIEW. NEWER, MORE
# EFFICIENT SOFTWARE HAS BEEN CREATED, WE KEEP THIS
# CODE FOR REFERENCE AND JUST IN CASE
#########################################################    
# ---
# This is deprecated, largely replaced by automon, we keep it for reference:
def showmon(request):
    domain	= request.get_host()
    host	= request.GET.get('host','')
    run		= request.GET.get('run','')
    subrun	= request.GET.get('subrun','')
    tpcmoncat	= request.GET.get('tpcmoncat','')
    ssprawcat	= request.GET.get('ssprawcat','')
    timingrawcat= request.GET.get('timingrawcat','')
    pdsphitmoncat	= request.GET.get('pdsphitmoncat','')

    url2images = settings.SITE['dqm_monitor_url']

    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")
    
    # This page serves two purposes - if the TPC monitor category
    # is defined, then it shows a page with graphics (depending
    # on the category. If there is no category provided, it shows
    # a choice of catogeries in a table.
    
    d = {}
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(domain, dqm_domain, domain)
    
    r6 = ("%06d"%int(run))
    s3 = ("%03d"%int(subrun))
    
    if(ssprawcat!=''):
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= 'SSP raw decoder  -- run:'+run+' subrun:'+subrun
        d['rows'] = monrun.SSPRawImgURLs(domain, url2images, j_uuid, r6, s3)
        return render(request, 'unitable3.html', d)

    if(timingrawcat!=''):
        item	= monrun.ALLmonitor('timingrawdecoder', int(timingrawcat))
        cat	= item[0]
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= cat+'  -- run:'+run+' subrun:'+subrun
        d['rows'] = monrun.TimingRawImgURLs(domain, url2images, j_uuid, r6, s3)
        return render(request, 'unitable3.html', d)

        
    if(tpcmoncat!=''):
        item	= monrun.ALLmonitor('tpc', int(tpcmoncat))
        cat	= item[0]
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= cat+'  -- run:'+run+' subrun:'+subrun

        Ncat = int(tpcmoncat)
        if Ncat in (0,1,2,3,6,7,8):
           d['rows'] = monrun.TPCmonitorURLplanes('tpc', Ncat, domain, url2images, j_uuid, r6, s3)
        elif Ncat in (4,5,9,10):
            d['rows'] = monrun.TPCmonitorURLind(Ncat, domain, url2images, j_uuid, r6, s3)
        else:
           pass
        
        return render(request, 'unitable3.html', d)
    # ---
    if(pdsphitmoncat!=''):
        item	= monrun.ALLmonitor('pdsphit', int(pdsphitmoncat))
        cat	= item[0]
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= cat+'  -- run:'+run+' subrun:'+subrun

        Ncat = int(pdsphitmoncat)
        if Ncat in (0,1,2,3,4,5,6):
           d['rows'] = monrun.TPCmonitorURLplanes('pdsphit', Ncat, domain, url2images, j_uuid,  r6 , s3)
        else:
           pass
        
        return render(request, 'unitable3.html', d)
    # - we just served a graphic page according to the chosen category

    # ------------------
    # this table presents the categories available (clickable)
    d['tblHeader']	= 'Run:'+run+' subrun:'+subrun

    d['tables']		= []
    
    t = ShowMonTable(monrun.TPCmonitorCatURLs(domain, run, subrun))
    t.changeName('TPC monitor items')
    d['tables'].append(t)
    
    t2 = ShowMonTable(monrun.PDSPHITmonitorCatURLs(domain, run, subrun))
    t2.changeName('PDSP HIT monitor items')
    d['tables'].append(t2)
    
    t3 = ShowMonTable(monrun.TimingRawCatURLs(domain, run, subrun))
    t3.changeName('Timing Raw Decoder and SSP raw decoder')
    d['tables'].append(t3)

    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain)

    return render(request, 'unitable3.html', d)
    
#########################################################    
@csrf_exempt
def plot18(request):
    domain	= request.get_host()
    run		= request.GET.get('run','')
    return HttpResponse('work in progress')
##################################################################

#########################################################    
@csrf_exempt
def eventdisplay(request):
    
    domain	= request.get_host()
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')

    d = {}

    d['display'] = (event!='' and run!='')
    d['chList'] = ('0-2559','2560-5119','5120-7679','7680-10239','10240-12799','12800-15359')

    d['domain']		= domain
    d['evdispURL']	= 'evdisp'
    d['run']		= run
    d['event']		= event
    
    d['pageName']	= ': Event Display'
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(domain, dqm_domain)

    return render(request, 'display.html', d)

#########################################################    
############# EVENT DISPLAY #############################    
#########################################################    
@csrf_exempt
def display6(request):
    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    
    domain	= request.get_host()
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')


    objs = evdisp.objects.filter(run=run).filter(evnum=event)
    
    d = {}
    d['domain']		= domain
    d['changroups']	= [1,2,3,4,5,6]

    ts = None
    d['rows'] = []
    for N in d['changroups']:
        raw	= objs.filter(changroup=N).filter(datatype='raw')[0]
        prep	= objs.filter(changroup=N).filter(datatype='prep')[0]

        ts = raw.ts
        rawUrl = ('http://%s/%s/%s/%s'
                         % (domain, # this needs to point to the image, also below
                            settings.SITE['dqm_evdisp_url'],
                            raw.j_uuid,
                            evdisp.makename(int(event), 'raw', N)
                         ))

        prepUrl = ('http://%s/%s/%s/%s'
                         % (domain, # this needs to point to the image, also below
                            settings.SITE['dqm_evdisp_url'],
                            raw.j_uuid,
                            evdisp.makename(int(event), 'prep', N)
                         ))
        d['rows'].append([rawUrl,prepUrl])

    d['run']		= run
    d['event']		= event
    d['ts']		= ts
    d['pageName']	= ': Event Display'
    d['message']	= evdisp.message()
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain)
    
    return render(request, 'display6.html', d)

#########################################################    
@csrf_exempt
def display1(request):
    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    
    domain	= request.get_host()
    url		= request.GET.get('url','')
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')
    changroup	= request.GET.get('changroup','')
    datatype	= request.GET.get('datatype','')

    d = {}
    d['domain']		= domain

    for item in ('url', 'run', 'event', 'changroup', 'datatype'):
        stuff = request.GET.get(item,'')
        if(item=='changroup'):
            d[item] = stuff+' ('+evdisp.group2string(int(stuff))+')'
        else:
            d[item]	= stuff
    
    d['pageName']	= ': Event Display'
    d['message']	= evdisp.message()
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain)
    
    return render(request, 'display1.html', d)
#########################################################    
# purStr += ('[new Date(%s), %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), forChart.lifetime)

