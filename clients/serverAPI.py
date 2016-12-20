from comms		import data2post, rdec, communicate
from serverURL		import serverURL
########################################################################
def registerWorkflow(allUrls, dag, name, description):
    d ={'dag':dag, 'name':name, 'description':description}

    wfData	= data2post(d).utf8()
    return rdec(communicate(allUrls['workflow']['addwfURL'], wfData))
