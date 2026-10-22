#!/usr/bin/env python3
"""NEXUS read-only adapter. Python3.9+, standard library. No demo fallback."""
import argparse,copy,hmac,json,math,os,threading,time,urllib.parse,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

MAX_BODY=2*1024*1024
FIELDS=('cpu_percent','memory_used','memory_total','memory_available','disk_used','disk_total','disk_free')
AI=('worker','queued','active','done','failed','web','sources','diagnostics')
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):return None

def number(v):
    if isinstance(v,bool):return None
    try:n=float(v)
    except (ValueError,TypeError):return None
    return n if math.isfinite(n) else None

def current(t,now,ttl=180):
    return number(t) is not None and 0<=now-float(t)<=ttl

def json_request(url,data=None,token=None):
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Configure a fixed HTTP(S) URL without embedded credentials')
    headers={'Accept':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    encoded=None if data is None else json.dumps(data).encode()
    if encoded:headers['Content-Type']='application/json'
    req=urllib.request.Request(url,encoded,headers,method='GET' if data is None else 'POST')
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=6) as r:
        raw=r.read(MAX_BODY+1)
        if len(raw)>MAX_BODY:raise ValueError('Upstream response too large')
    return json.loads(raw)

def item_ids(cfg):
    ids=set()
    for s in cfg.get('servers',[]):
        ids.update(s.get('items',{}).values())
        for d in s.get('disks',[]):ids.update(d.get('items',{}).values())
    for c in cfg.get('checks',[]):ids.update(c.get('items',{}).values())
    ids={str(i) for i in ids}
    if len(ids)>100:raise ValueError('At most 100 explicitly configured item IDs')
    if any(not i.isdecimal() for i in ids):raise ValueError('Item IDs must be decimal strings')
    return ids

def sample(items,iid,now):
    r=items.get(str(iid),{})
    n=number(r.get('lastvalue'));t=number(r.get('lastclock'))
    if str(r.get('state','1'))!='0' or str(r.get('status','1'))!='0' or not current(t,now):return None
    return {'value':n,'checked_at':t} if n is not None else None

def projection(cfg,items,now):
    servers=[]
    for row in cfg.get('servers',[])[:5]:
        s={k:str(row.get(k,''))[:300] for k in ('id','name','role','address','note')};s['source']='Configured Zabbix item observations';s['metrics']={}
        for k,iid in row.get('items',{}).items():
            if k not in FIELDS:continue
            v=sample(items,iid,now)
            if v and (v['value']<0 or k=='cpu_percent' and v['value']>100):v=None
            if v:s['metrics'][k]=v
        # Infer used from total-minus-available only when both observations are current.
        if 'memory_used' not in s['metrics']:
            a,b=s['metrics'].get('memory_available'),s['metrics'].get('memory_total')
            if a and b and 0<=a['value']<=b['value'] and abs(a['checked_at']-b['checked_at'])<=60:
                s['metrics']['memory_used']={'value':b['value']-a['value'],'checked_at':min(a['checked_at'],b['checked_at'])}
        s['disks']=[]
        for d in row.get('disks',[])[:3]:
            a=sample(items,d.get('items',{}).get('used'),now);b=sample(items,d.get('items',{}).get('total'),now)
            if a and b and b['value']>0 and 0<=a['value']<=b['value'] and abs(a['checked_at']-b['checked_at'])<=60:s['disks'].append({'name':str(d.get('name','Pool'))[:80],'used':a['value'],'total':b['value'],'checked_at':min(a['checked_at'],b['checked_at'])})
        servers.append(s)
    checks=[]
    for c in cfg.get('checks',[])[:24]:
        values={k:sample(items,i,now) for k,i in c.get('items',{}).items()};failed=values.get('failed_step');code=values.get('http_code');latency=values.get('response_seconds')
        known=failed is not None and all(v is not None for v in values.values())
        expected=c.get('expected_status',200)
        passing=known and failed['value']==0 and (code is None or code['value']==expected)
        t=min((v['checked_at'] for v in values.values() if v),default=0)
        checks.append({'name':str(c.get('name','Check'))[:120],'company':str(c.get('company',''))[:80],'state':'unknown' if not known else 'passing' if passing else 'failing','checked_at':t,'expected_status':expected,'http_code':code['value'] if code else None,'response_seconds':latency['value'] if latency else None})
    return servers,checks

class Collector:
    def __init__(self,cfg,fetch=json_request):
        self.cfg=cfg;self.fetch=fetch;self.lock=threading.Lock();self.snapshot={};self.ids=item_ids(cfg)
        if len(cfg.get('servers',[]))>5 or len(cfg.get('checks',[]))>24:raise ValueError('Limit five servers and24checks')
        keys=[s.get('id') for s in cfg.get('servers',[])]
        if any(not isinstance(k,str) or not k for k in keys) or len(set(keys))!=len(keys):raise ValueError('Server IDs must be unique nonempty strings')
    def collect(self,now=None):
        now=time.time() if now is None else now
        out={'version':1,'checked_at':now,'stale':False,'coverage':{},'summary':{'open':None,'unknown':None,'restore_validated':False},'servers':{'servers':[]},'business':{'checks':[]},'readiness':[],'incidents':[],'ai':{},'topology':{'links':self.cfg.get('links',[])[:24]}}
        z=self.cfg.get('zabbix',{});ok=False
        if z.get('url') and self.ids and os.environ.get('NEXUS_ZABBIX_TOKEN'):
            try:
                resp=self.fetch(z['url'],{'jsonrpc':'2.0','id':1,'method':'item.get','params':{'itemids':sorted(self.ids),'webitems':True,'output':['itemid','lastvalue','lastclock','state','status']}},os.environ['NEXUS_ZABBIX_TOKEN'])
                if 'error' in resp:raise ValueError('Zabbix API request failed')
                items={str(i['itemid']):i for i in resp['result']};out['servers']['servers'],out['business']['checks']=projection(self.cfg,items,now);ok=True
            except Exception:pass # No endpoint, credentials or upstream bodies in public diagnostics.
        out['coverage']['zabbix']={'ok':ok,'complete':ok}
        p=self.cfg.get('prometheus',{});queries=p.get('queries',{});gate=p.get('freshness_expression');ai={};prom_ok=False
        if p.get('url') and gate and queries:
            try:
                for k,expr in queries.items():
                    if k not in AI:continue
                    q='('+expr+') and on() ('+gate+')'
                    resp=self.fetch(p['url'].rstrip('/')+'/api/v1/query?'+urllib.parse.urlencode({'query':q,'time':str(now)}),None,os.environ.get('NEXUS_PROMETHEUS_TOKEN'))
                    if resp.get('status')!='success' or resp.get('data',{}).get('resultType')!='vector':raise ValueError('Expected successful instant vector')
                    rows=resp['data']['result']
                    if len(rows)==1:
                        stamp,value=rows[0]['value'];n=number(value)
                        if n is not None and n>=0 and current(number(stamp),now,120):ai[k]=n
                prom_ok=True
            except Exception:ai={}
        if ai:ai['checked_at']=now
        out['ai']=ai;out['coverage']['prometheus']={'ok':prom_ok,'complete':prom_ok}
        archive_ok=False
        if self.cfg.get('archive_file'):
            try:
                path=Path(self.cfg['archive_file'])
                if path.stat().st_size>65536:raise ValueError('Archive evidence file too large')
                r=json.loads(path.read_text());archive_ok=current(r.get('checked_at'),now)
                if archive_ok:
                    for v in r.get('readiness',[])[:10]:
                        t=number(v.get('timestamp'));state=v.get('state')
                        if t is not None and 0<t<=now and state in ('recent','verified','old','unknown'):out['readiness'].append({'name':str(v.get('name','Archive'))[:120],'timestamp':t,'state':state})
            except Exception:pass
        out['coverage']['backups']={'ok':archive_ok,'complete':archive_ok}
        with self.lock:self.snapshot=out
        return out
    def get(self,now=None):
        now=time.time() if now is None else now
        with self.lock:out=copy.deepcopy(self.snapshot)
        out['stale']=not current(out.get('checked_at'),now,120)
        return out

def make_handler(collector,token):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ('/snapshot','/healthz'):self.send_error(404);return
            if token and not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+token):self.send_error(401);return
            body=json.dumps(collector.get() if self.path=='/snapshot' else {'ok':not collector.get().get('stale',True)},allow_nan=False).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_POST(self):self.send_error(405)
        def do_PUT(self):self.send_error(405)
        def do_DELETE(self):self.send_error(405)
        def log_message(self,*args):pass
    return Handler

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--bind',default='127.0.0.1');p.add_argument('--port',type=int,default=8096);a=p.parse_args();token=os.environ.get('NEXUS_ADAPTER_TOKEN','')
    if a.bind not in ('127.0.0.1','::1','localhost') and not token:p.error('Non-loopback binding requires NEXUS_ADAPTER_TOKEN')
    collector=Collector(json.loads(Path(a.config).read_text()));collector.collect()
    def loop():
        while True:time.sleep(60);collector.collect()
    threading.Thread(target=loop,daemon=True).start();print('NEXUS read-only adapter started; configuration and credentials are never served.',flush=True)
    ThreadingHTTPServer((a.bind,a.port),make_handler(collector,token)).serve_forever()
if __name__=='__main__':main()
