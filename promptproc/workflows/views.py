###################################################
############ WORKFLOWS VIEWS ######################
###################################################
import os
import json

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone

import io
import uuid
import networkx as nx
from networkx.readwrite import json_graph

from .models import dag, dagVertex, dagEdge
from .models import workflow # wfVertex, wfEdge

from jobs.models	import job
from data.models	import dataset, datatype
from logic.models	import manager


def init(request):
    d = dag(name='test')
    if(dag._init):
        status = 'initialized'
    else:
        status = 'not initialized'
    dag._init = True
    return HttpResponse("WF INIT %s %s" % (d, status))

#########################################################
####### PART 1: DELETION AND OTHER SIMPLE STUFF #########
#########################################################

###################################################
# DELETE ALL -
# SHOULD ONLY BE USED BY EXPERTS, do not advertise
def deleteall(request):
    what = request.GET.get('what','')
    if(what==''):
        return HttpResponse("DELETE ALL: SPECIFICATION OF OBJECTS TO BE DELETED MISSING")


    ### ALL OF THIS WILL NEED TO BE IMPROVED WITH FOREIGN KEYS AND ALL -
    ### WRITTEN THIS WAY TO GET TO SPEED.
    success = True
    if(what=='dag'): 
        try:
            dag.objects.all().delete()
        except:
            success = False
        try:
            dagVertex.objects.all().delete()
        except:
            success = False
        try:
            dagEdge.objects.all().delete()
        except:
            success = False

    if(what=='workflow'): 
        try:
            # wfVertex.objects.all().delete()
            job.objects.all().delete()
        except:
            success = False
        try:
            # wfEdge.objects.all().delete()
            dataset.objects.all().delete()
        except:
            success = False
        try:
            workflow.objects.all().delete()
        except:
            success = False

    if(success):
        return HttpResponse("Deleted ALL %s" % what )
    else:
        return HttpResponse("Problems deleting ALL %s" % what )


###################################################
@csrf_exempt
def delete(request):
    post	= request.POST
    what	= post['what']
    
    keyname	= ''
    
    success = True
    
    if(what=='dag'):
        keyname = post['name']
        success	= deldag(keyname)

    if(what=='workflow'):
        keyname	= post['uuid']
        success	= delwf(keyname)
        
    if(success):
        return HttpResponse("Deleted %s %s" % (what, keyname) )
    else:
        return HttpResponse("Problems deleting %s %s" % (what, keyname) )

 
###################################################
def delwf(wfuuid):
    success = True
    try:
        w = workflow.objects.get(uuid=wfuuid)
        w.delete()
    except:
        success = False
    try:
        for j in job.objects.filter(wfuuid=wfuuid): j.delete()
    except:
        success = False
    try:
        for ds in dataset.objects.filter(wfuuid=wfuuid): ds.delete()
    except:
        success = False

    return success

###################################################
def deldag(name):
    success = True
    try:
        d = dag.objects.get(name=name)
        d.delete()
    except:
        success = False
    try:
        for v in dagVertex.objects.filter(dag=name): v.delete()
    except:
        success = False
    try:
        for e in dagEdge.objects.filter(dag=name): e.delete()
    except:
        success = False
        
    return success
###################################################
@csrf_exempt
def adddag(request):
    
    post	= request.POST

    name	= post['name']
    graphml	= post['graphml']
    description	= post['description']

    x = deldag(name)

    tmpdir = '/tmp/p3s/'
    if(not os.path.exists(tmpdir)):
        try:
            os.makedirs(tmpdir)
        except:
            exit(-1) # we can't proceed

    fn = tmpdir+name+".graphml"
    f = open(fn, "w") # FXIME: this has yet to work: f = io.StringIO()
    f.write(graphml)
    f.close()

    
    f = open(fn, "r")
    g = nx.read_graphml(f)

    ts_def   = timezone.now()
    vertices = nx.topological_sort(g) # print('*****',vertices)

    v_list = []
    for v in vertices:
        v_list.append(v)
    
    newDag		= dag()
    newDag.name		= name
    newDag.description	= description
    newDag.nvertices	= len(v_list)
    newDag.ts_def	= ts_def
    newDag.root		= v_list[0]
    newDag.save()

    dvFields = []
    for f in dagVertex._meta.get_fields():dvFields.append(f.name)
    
    for n in g.nodes(data=True):
        dv = dagVertex()
        dv.name  = n[0]
        dv.dag   = name
        dicto = n[1]
        for k in dicto.keys():
            if k in dvFields:
                dv.__dict__[k]=dicto[k]
        dv.save()
        
    deFields = []
    for f in dagEdge._meta.get_fields():deFields.append(f.name)

    for e in g.edges(data=True):
        de = dagEdge()
        de.source = e[0]
        de.target = e[1]
        de.name	  = e[2]['name']
        de.dag    = name
        dicto = e[2]
        for k in dicto.keys():
            if k in deFields:
                de.__dict__[k]=dicto[k]
        de.save()

    return HttpResponse("RESPONSE %s" % graphml )

###################################################
def getdag(request):
    name = request.GET.get('name','')

    if(name == ''): return HttpResponse("DAG not specified.")
    g = fetchdag(name)
    s = '\n'.join(nx.generate_graphml(g))
    return HttpResponse(s)

###################################################
def fetchdag(dag): # inflate DAG from RDBMS
    g = nx.DiGraph()
    
    for dv in dagVertex.objects.filter(dag=dag):
        g.add_node(dv.name)
        
    for de in dagEdge.objects.filter(dag=dag):
        g.add_edge(de.source, de.target)

    return g


#########################################################
########## PART 2: GENERATE WORKFLOW      ###############
#########################################################

###################################################
@csrf_exempt
def addwf(request):

    fileinfo	= None
    jobinfo	= None
    sticky	= False
    inherit	= None
    
    post	= request.POST
    dagName	= post['dag']
    name	= post['name']
    state	= post['state']
    filejson	= post['fileinfo']
    jobjson	= post['jobinfo']
    description	= post['description']
    wfuuid	= uuid.uuid1()

    if(filejson!=''):
        try:
            fileinfo = json.loads(filejson)
        except: # non-JSON string... Identify:
            if(filejson=='sticky'):
                sticky = True
            if('inherit' in filejson):
                try:
                    inherit = filejson.split(':')[1]
                except:
                    pass
                    
    if(jobjson!=''):	jobinfo = json.loads(jobjson)

    # print(jobjson)
    # print(jobinfo)
    
    ts_def   = timezone.now()

    rootName = dag.objects.get(name=dagName).root

    # Create a Workflow object and populate it:
    wf		= workflow()
    wf.ts_def	= ts_def
    wf.uuid	= wfuuid
    wf.dag	= dagName
    wf.name	= name
    wf.state	= state
    wf.description= description
    # ATTN: we'll save the WF a bit later ( we would like to get the root job uuid).

    g = nx.DiGraph()

    # +++++++++ JOBS
    for dv in dagVertex.objects.filter(dag=dagName):
        g.add_node(dv.name, wf=dagName)
        
	# defaults:
        payload	= dv.payload
        env	= dv.env
        if(jobinfo):		# need to overwrite some attributes
            for k in jobinfo.keys():
                if(k== dv.name):
                    try:
                        payload=jobinfo[k]["payload"]
                    except:
                        pass
                    try:
                        env=json.dumps(jobinfo[k]["env"])
                    except:
                        pass
                    
        j = job(
            uuid		= uuid.uuid1(),
            wfuuid		= wfuuid,
            jobtype		= dv.jobtype,
            payload		= payload,
            env			= env,
            priority		= dv.priority,
            state		= 'template',
            ts_def		= ts_def,
            timelimit		= dv.timelimit,
            name		= dv.name,
        )

        if(dv.name == rootName): wf.rootuuid = j.uuid
        j.save()
    # +++++++++ END JOBS
    
    wf.save() # can do it now since needed rootuuid, now we have it

    # +++++++++ DATA
    for de in dagEdge.objects.filter(dag=dagName):
        
        # even in a multigraph, an edge can only be associated with one
        # source and one target. A source and a target can be connected
        # by multiple edges in a multigraph, however. So check for
        # the former condition.
        
        s_cand = job.objects.filter(wfuuid=wfuuid, name=de.source)
        t_cand = job.objects.filter(wfuuid=wfuuid, name=de.target)
        
        if(len(s_cand)!=1): return HttpResponse("addwf: inconsistent graph - source")
        if(len(t_cand)!=1): return HttpResponse("addwf: inconsistent graph - target")
        
        sourceuuid = s_cand[0].uuid
        targetuuid = t_cand[0].uuid

        # a "dataset" - a file in this case - is created by default with a name formed
        # from its UUID and predefined extension (as per type object)
        # BUT! can be overridden by "fileinfo"

        # defaults
        d_uuid	= str(uuid.uuid1())
        dt = ''
        try:
            dt	= datatype.objects.get(name=de.datatype)
        except:
            delstat = ''
            if delwf(wfuuid):
                delstat ='OK'
            else:
                delstat = 'FAIL'
            return HttpResponse('Failed to get datatype, deleting workflow. Clean up status: %s' % delstat)

        ext	= dt.ext # expect that the dot is included
        
        dirpath	= de.dirpath
        
        filename= ''
        if(sticky):
            filename = de.name
        elif(inherit):
            filename = inherit+':'+dagName+':'+de.source+':'+de.datatag+ext
            print(filename)
        else:
            filename = d_uuid+ext
            
        comment	= de.comment # default comment in herited from DAG

        # Optional overrides: client sends JSON data with "updates"
        if(fileinfo):
            for k in fileinfo.keys():
                if((de.source+":"+de.target)==k):
                    try:
                        filename=fileinfo[k]["name"]
                    except:
                        pass
                    try:
                        dirpath	=fileinfo[k]["dirpath"]
                    except:
                        pass
                    try:
                        comment	=fileinfo[k]["comment"]
                    except:
                        pass
                        
        d = dataset(
            uuid	= d_uuid,
            wfuuid	= wfuuid,
            source	= de.source,
            target	= de.target,
            sourceuuid	= sourceuuid,
            targetuuid	= targetuuid,
            name	= filename,
            state	= 'template',
            dirpath	= dirpath,
            comment	= comment,
            datatype	= de.datatype,
            datatag	= de.datatag,
            wf     	= name,
        )

        d.save()
        g.add_edge(de.source, de.target)
        
        # +++ AUGMENT JOB ENVIRONMENT WITH DATASET INFO
        fullname=dirpath+filename
        
        #print('source:',de.source,' target:', de.target,' datatag:', de.datatag, ' full name:',fullname)

        for jid in (sourceuuid, targetuuid):
            j4env = job.objects.get(uuid=jid) # MUST work as per comments above, we checked
            j4env.augmentEnv({de.datatag:fullname})
            j4env.save()
       
        
    # +++++++++ END DATA


    
    # Now that the WF is created, is can be set into defined state
    # (hence ready for execution) if so desired. This method
    # toggles both wf and its "root job"
    
    if(state=='defined'):wf2defined(wf)

    # Finish up and send  message to the client
    s = '\n'.join(nx.generate_graphml(g)) # this can be in fact something else
    return HttpResponse(s)
    
###################################################
# Set 'defined' state of the workflow, which
# includes setting 'defined' state of the root job
#
# Note that this is normally set by a client and
# not by some sort of event, which makes it
# different from a similar line of code in
# the pilot view
#
def wf2defined(wf):
    wf.state	= 'defined'
    wf.save()
    
    j = job.objects.get(uuid=wf.rootuuid)
    
    if(j.jobtype=='noop'):
        j.state = 'finished'
        manager.childrenStateToggle(j,'defined')
    else:
        j.state = 'defined'
    j.save()
###################################################
@csrf_exempt
def setwfstate(request):
    post	= request.POST
    wfuuid	= post['uuid']
    state	= post['state']

    # print('setting state: %s %s' % (wfuuid, state))
    
    wf = workflow.objects.get(uuid=wfuuid)
    
    if(state=='defined'):
        wf2defined(wf)
    else:
        # FIXME: obviously needs more work, not general enough
        wf.state=state
        wf.save()
    
    return HttpResponse(state)
################ DUSTY ATTIC ######################
# d0 = json_graph.node_link_data(g)
# d1= json_graph.adjacency_data(g)
