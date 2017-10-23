
######################## DUSTY ATTIC ###################################
#
# CONTAINS RANDOM BITS OF CODE THAT HAVE BEEN PHASE OUT, JUST FOR REFERENCE
#
#-------------pilot.py
#
# a) --- process management... deferred 4.6.2017
# import psutil
#---
# b) Looking for children:
#            errCode = proc.poll()
#            psProc = psutil.Process(pid=jobPID)
#            psKids=psProc.children(recursive=True)
#            if(verb>1): print(psKids)
#---
# c) Decomissioned way of starting jobs
# else: # Deprecated...
#     try:
#         x=subprocess.run([payload], stdout=subprocess.PIPE)
#         if(verb>1): logger.info('job output: %s' % x.stdout.decode("utf-8"))
#         p['state']	='finished'
#         p['event']	='jobstop'
#         p['jobcount']  += 1
#         response = API.reportPilot(p)
#         logger.info('JOB finished: %s' %  p['job'])
#     except:
#         p['state']	='exception'
#         p['event']	='exception'
#         response = API.reportPilot(p)
#         logger.info('JOB exception: %s' %  p['job'])
#---
# d) Handling pipes from the process, now deprecated:
# they just fill up too soon (short buffers)
#
# jobout = open(joblogdir+'/'+ p['job']+'.out','w')
# joberr = open(joblogdir+'/'+ p['job']+'.err','w')
# jobout.write((proc.stdout.read().decode('utf-8')))
# joberr.write((proc.stderr.read().decode('utf-8')))
