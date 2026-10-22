#!/usr/bin/env python3
"""Generate two portable Classic-model dashboards, with no private environment inputs."""
import argparse,json
from pathlib import Path
from fixture import fixture,T
ROOT=Path(__file__).resolve().parent
INF={'type':'yesoreyeram-infinity-datasource','uid':'${DS_OPERATIONS}'}
PROM={'type':'prometheus','uid':'${DS_PROMETHEUS}'}

def datasource_var(name,label,plugin):return {'name':name,'label':label,'type':'datasource','query':plugin,'current':{},'options':[],'refresh':1,'hide':0,'multi':False,'includeAll':False}
def snapshot(demo):
    q={'refId':'A','datasource':INF,'type':'json','source':'inline' if demo else 'url','format':'table','parser':'backend','root_selector':'','columns':[{'selector':'checked_at','text':'checked_at','type':'number'}],'filters':[]}
    if demo:q['data']=json.dumps(fixture(),separators=(',',':'))
    else:q.update(url='${adapter_url}',url_options={'method':'GET','data':''})
    return q

def build(demo):
    panels=[]
    def panel(typ,title,x,y,w,h,options,targets=None,ds=INF):
        p={'id':len(panels)+1,'type':typ,'title':('[DEMO] ' if demo else '')+title,'gridPos':{'x':x,'y':y,'w':w,'h':h},'transparent':True,'fieldConfig':{'defaults':{'noValue':'UNKNOWN'},'overrides':[]},'options':options}
        if targets:p.update(datasource=ds,targets=targets)
        panels.append(p);return p
    def chart(name,title,x,y,w,h):
        code='const NEXUS_DEMO='+str(demo).lower()+';\nconst NEXUS_FIXTURE='+json.dumps(fixture() if demo else None)+';\n'+(ROOT/'charts/core.js').read_text()+'\n'+(ROOT/f'charts/{name}.js').read_text()
        return panel('volkovlabs-echarts-panel',title,x,y,w,h,{'editorMode':'code','getOption':code,'renderer':'canvas','map':'none'},None if demo else [snapshot(False)])
    panel('text','COMMUNITY EDITION / START HERE',0,0,24,4,{'mode':'markdown','content':('**SYNTHETIC DEMO — no live data.** All displayed values, incidents, names and histories are fictional. Fixture clock is fixed to January1,2026. Embedded fixture makes no datasource or monitoring requests. Install Business Charts 7.2.5; no datasource setup is required. ' if demo else '**LIVE ADAPTER EDITION.** Select your Infinity and Prometheus datasources above; set Adapter URL to your fixed read-only endpoint. Configure the same origin in Infinity allowedHosts. Optional bearer auth belongs in datasource settings, never dashboard variables. Missing or stale data stays unknown. ')+'\n\n**IZEX NEXUS · Kingsley Izex / IZEX Solutions · MIT source.** Five configurable servers; up to24checks; declared dependencies; normalized AI activity; archive evidence. This is a community dashboard, not a vendor plugin or certification. Install/runbook/schema are included in the release package. Latest-value instruments ignore the historical time picker; history panels follow it. Resize for your display.'})
    chart('header','NEXUS / UNIFIED OBSERVABILITY',0,4,24,5)
    chart('fleet','COMPUTE / INSTRUMENT CLUSTER',0,9,24,7)
    chart('constellation','DEPENDENCIES / EVIDENCE COVERAGE',0,16,12,13)
    chart('business','BUSINESS / SERVICE FABRIC',12,16,12,13)
    chart('ai','INTELLIGENCE / WORK OBSERVED',0,29,12,12)
    chart('recovery','RECOVERY / ARCHIVE EVIDENCE',12,29,12,12)
    if demo:
        for x,title,series in [(0,'FICTIONAL CPU HISTORY',[('Example pod A',[.1,.12,.09,.18,.15,.11]),('Example pod B',[.2,.25,.22,.2,.29,.24])]),(12,'FICTIONAL QUEUE HISTORY',[('Example queued',[1,2,3,2,4,3]),('Example processing',[1,1,0,1,1,1])])]:
            code="const C=['#46ebc0','#b29cff']; return {animation:false,backgroundColor:'#080f1e',aria:{enabled:true},title:{text:'SYNTHETIC DEMO / FIXED ILLUSTRATION',textStyle:{fontSize:12,color:'#ffcd70'}},tooltip:{trigger:'axis'},legend:{bottom:0,textStyle:{color:'#91a6bc'}},grid:{left:55,right:25,top:45,bottom:55},xAxis:{type:'category',data:['T−5','T−4','T−3','T−2','T−1','T']},yAxis:{type:'value',min:0},series:"+json.dumps([{'name':n,'type':'line','data':v,'smooth':False} for n,v in series])+".map((s,i)=>({...s,itemStyle:{color:C[i]}}))};"
            panel('volkovlabs-echarts-panel',title,x,41,12,9,{'editorMode':'code','getOption':code,'renderer':'canvas','map':'none'})
    else:
        gate='(up{job="${ai_job}"} == 1) and on() (time()-izex_ai_snapshot_timestamp_seconds >= 0) and on() (time()-izex_ai_snapshot_timestamp_seconds < 120)'
        expressions=[(0,'KUBERNETES / CONTAINER CPU CORES','sum by (pod) (rate(container_cpu_usage_seconds_total{namespace=~"${namespaces:regex}",container!="",container!="POD"}[5m]))','{{pod}}','cores'),(12,'AI / QUEUED + ACTIVE JOBS','izex_ai_jobs{status=~"queued|processing"} and on() ('+gate+')','{{workflow}} / {{status}}','short')]
        for x,title,expr,legend,unit in expressions:
            p=panel('timeseries',title,x,41,12,9,{'legend':{'displayMode':'table','placement':'bottom','calcs':['lastNotNull']},'tooltip':{'mode':'multi'}},[{'refId':'A','datasource':PROM,'expr':expr,'range':True,'instant':False,'legendFormat':legend}],PROM)
            p['fieldConfig']['defaults'].update(unit=unit,min=0,color={'mode':'palette-classic'},custom={'drawStyle':'line','lineWidth':2,'fillOpacity':10,'showPoints':'never','spanNulls':False})
    chart('incidents','OPERATIONS / INCIDENT EVIDENCE',0,50,12,12)
    chart('storage','STORAGE / CAPACITY PRESSURE',12,50,12,12)
    if demo:
        panel('text','REFERENCE / FICTIONAL INVENTORY',0,62,24,9,{'mode':'markdown','content':'**SYNTHETIC DATA — example names and addresses only.**\n\n| Server | Example address | Source |\n|---|---|---|\n'+'\n'.join('| '+s['name']+' | '+s['address']+' | Fictional fixture |' for s in fixture()['servers']['servers'])})
    else:
        t=snapshot(demo);t.update(root_selector='servers.servers',columns=[{'selector':k,'text':n,'type':'string'} for k,n in [('name','Server'),('address','Address'),('source','Source'),('note','Meaning')]])
        p=panel('table','REFERENCE / SOURCE SEMANTICS',0,62,24,9,{'showHeader':True,'cellHeight':'md','footer':{'show':False}},[t]);p['transformations']=[{'id':'organize','options':{'indexByName':{'Server':0,'Address':1,'Source':2,'Meaning':3}}}]
    panel('text','INTERPRETATION / LIMITATIONS',0,71,24,7,{'mode':'markdown','content':'**Grey / — means UNKNOWN, not zero.** Snapshot≤120s, complete source, host/check samples≤180s, no future clocks. CPU visual bands: <75% teal, 75–89.9% amber, ≥90% rose; display colors do not configure alerts. Dependencies are declared relationships, never measured traffic or proven causality.\n\nLinux RAM can be total−available; hypervisor memory differs from guest pressure. Pools, VM filesystems and shared volumes overlap: never sum them. Expected401 can pass; public checks do not prove private transactions. Archive/checksum evidence is not a restore test. AI outcomes are rolling retained-record gauges, not counters. Job completion and source citations do not prove semantic correctness.\n\nThe bundled adapter does not create alerts, repairs, backups or an incident feed. Its incident count stays unknown unless you supply an explicit incident projection in your own compatible adapter. Optional Prometheus history panels require the documented metrics. No live service or private network needs to be made public to publish this dashboard.'})
    vars=[] if demo else [datasource_var('DS_OPERATIONS','Infinity datasource','yesoreyeram-infinity-datasource')]
    if not demo:
        vars += [datasource_var('DS_PROMETHEUS','Prometheus datasource','prometheus'),{'name':'adapter_url','label':'Adapter URL','type':'textbox','current':{'text':'https://adapter.example.invalid/snapshot','value':'https://adapter.example.invalid/snapshot'},'options':[]},{'name':'ai_job','label':'AI scrape job','type':'textbox','current':{'text':'knowledge-library','value':'knowledge-library'},'options':[]},{'name':'namespaces','label':'Kubernetes namespaces','type':'custom','query':'default, monitoring','multi':True,'includeAll':True,'allValue':'.*','current':{'text':'All','value':'$__all'},'options':[{'text':'All','value':'$__all','selected':True}]}]
    d={'id':None,'uid':'izex-nexus-community-demo' if demo else 'izex-nexus-community-live','title':'IZEX NEXUS Community / '+('Synthetic Demo' if demo else 'Live Adapter'),'description':'Portable evidence-aware infrastructure, business and local AI observability by Kingsley Izex / IZEX Solutions. '+('All data is synthetic.' if demo else 'Requires the documented read-only adapter and optional Prometheus metrics.'),'tags':['IZEX','NEXUS','community','synthetic-demo' if demo else 'observability'],'schemaVersion':41,'version':1,'editable':True,'timezone':'browser','refresh':'' if demo else '1m','time':{'from':'now-6h','to':'now'},'templating':{'list':vars},'panels':panels,'annotations':{'list':[]},'links':[],'__requires':[{'type':'grafana','id':'grafana','name':'Grafana','version':'13.2.1'},{'type':'panel','id':'volkovlabs-echarts-panel','name':'Business Charts','version':'7.2.5'}]+([] if demo else [{'type':'datasource','id':'yesoreyeram-infinity-datasource','name':'Infinity','version':'4.1.1'},{'type':'datasource','id':'prometheus','name':'Prometheus','version':'1.0.0'}])}
    for a in panels:
        for b in panels:
            if a is b:continue
            x,y=a['gridPos'],b['gridPos'];assert not(x['x']<y['x']+y['w'] and y['x']<x['x']+x['w'] and x['y']<y['y']+y['h'] and y['y']<x['y']+x['h'])
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'dist');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    for demo,name in [(True,'nexus-community-demo.json'),(False,'nexus-community-live.json')]:
        d=build(demo);(a.out/name).write_text(json.dumps(d,indent=2)+'\n');print(name,len(d['panels']),'panels')
    (a.out/'schema-example.json').write_text(json.dumps(fixture(),indent=2)+'\n')
if __name__=='__main__':main()
