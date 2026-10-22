"""Deliberately fictional sample data. Never used by the live adapter."""
T=1767225600

def fixture():
    names=[('compute','Compute host','Virtualization'),('linux','Linux guest','Applications'),('containers','Container host','Monitoring'),('lab','Test VM','Isolated experiment'),('ai','AI workstation','Local inference')]
    servers=[]
    for i,(key,name,role) in enumerate(names):
        metrics={k:{'value':v,'checked_at':T} for k,v in {'cpu_percent':[24,36,14,4,58][i],'memory_used':[12,5,3,1,10][i]*2**30,'memory_total':[32,8,8,4,16][i]*2**30,'disk_used':[180,25,18,8,90][i]*2**30,'disk_total':[500,80,80,32,256][i]*2**30}.items()}
        servers.append({'id':key,'name':name,'role':role,'address':'host-'+key+'.example.invalid','source':'Fictional sample fixture','note':'SYNTHETIC: illustrative resource values, not an observation.','metrics':metrics,'disks':[]})
    servers[0]['disks']=[{'name':'VM pool','used':180*2**30,'total':500*2**30,'checked_at':T},{'name':'Archive pool','used':240*2**30,'total':1000*2**30,'checked_at':T}]
    checks=[{'name':f'{company} / {route}','company':company,'checked_at':T,'state':'passing','http_code':401 if route=='Auth boundary' else 200,'expected_status':401 if route=='Auth boundary' else 200,'response_seconds':.12+.027*i} for i,(company,route) in enumerate((c,r) for c in ['Example A','Example B'] for r in ['Homepage','Services','Login','Health','Auth boundary'])]
    return {'version':1,'checked_at':T,'stale':False,'coverage':{s:{'ok':True,'complete':True} for s in ['zabbix','prometheus','backups']},'summary':{'open':1,'unknown':0,'restore_validated':False},'servers':{'servers':servers},'business':{'checks':checks},'ai':{'checked_at':T,'worker':1,'queued':3,'active':1,'done':27,'failed':2,'web':8,'sources':6,'diagnostics':1},'readiness':[{'name':'Example VM archive','state':'recent','timestamp':T-86400},{'name':'Example application archive','state':'verified','timestamp':T-7200}], 'incidents':[{'id':'DEMO-001','status':'open','severity':'warning','title':'Fictional queue capacity review','test':False}], 'topology':{'links':[['compute','linux'],['compute','containers'],['compute','lab'],['linux','ai']]}}
