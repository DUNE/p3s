#########################################################    
def parseCommaDash(inp):
    outlist = []
    if('-' in inp):
        left_right = inp.split('-')
        for x in range(int(left_right[0]), int(left_right[1])+1):
            outlist.append(x)
    elif(',' in inp):
        outlist=inp.split(',')
    else:
        outlist.append(int(inp))
        
    return outlist
#########################################################    
def makeTupleList(listOfStuff):
    theList = []
    for stuff in listOfStuff: theList.append((stuff,stuff))
    return theList

