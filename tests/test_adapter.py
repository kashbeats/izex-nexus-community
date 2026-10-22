import importlib.util,json,os,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
spec=importlib.util.spec_from_file_location('adapter',Path(__file__).parents[1]/'adapter/server.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
NOW=1767225600
CFG={'zabbix':{'url':'https://monitor.example.invalid/api_jsonrpc.php'},'servers':[{'id':'a','name':'Host','items':{'cpu_percent':'1','memory_available':'2','memory_total':'3'}}],'checks':[{'name':'Guard','expected_status':401,'items':{'failed_step':'4','http_code':'5'}}]}
def item(i,v,clock=NOW,state='0'):return {'itemid':str(i),'lastvalue':str(v),'lastclock':str(clock),'state':state,'status':'0'}
class AdapterTests(unittest.TestCase):
 def test_freshness_and_invalid_values(self):
  for bad in [None,NOW+1,NOW-181,'bad']:self.assertFalse(a.current(bad,NOW))
  for bad in ['NaN',float('inf'),True,None]:self.assertIsNone(a.number(bad))
 def test_cache_clock_expiry(self):
  c=a.Collector({});c.collect(NOW);self.assertTrue(c.get(NOW+121)['stale']);self.assertTrue(c.get(NOW-1)['stale'])
 def test_resource_semantics_and_guard(self):
  rows={str(i):item(i,v) for i,v in [(1,0),(2,3),(3,8),(4,0),(5,401)]};s,c=a.projection(CFG,rows,NOW)
  self.assertEqual(s[0]['metrics']['cpu_percent']['value'],0);self.assertEqual(s[0]['metrics']['memory_used']['value'],5);self.assertEqual(c[0]['state'],'passing')
  rows['5']=item(5,401,NOW-181);self.assertEqual(a.projection(CFG,rows,NOW)[1][0]['state'],'unknown')
 def test_future_or_unsupported_item_is_unknown(self):
  for r in [item(1,30,NOW+1),item(1,30,state='1'),item(1,120)]:
   s,_=a.projection(CFG,{'1':r},NOW);self.assertNotIn('cpu_percent',s[0]['metrics'])
 def test_upstream_failure_does_not_reuse_old_green(self):
  def fetch(*args):raise ValueError('sensitive upstream details')
  with patch.dict(os.environ,{'NEXUS_ZABBIX_TOKEN':'test-secret'}):out=a.Collector(CFG,fetch).collect(NOW)
  self.assertFalse(out['coverage']['zabbix']['ok']);self.assertEqual(out['servers']['servers'],[]);self.assertNotIn('test-secret',json.dumps(out));self.assertNotIn('sensitive',json.dumps(out))
 def test_prometheus_gate_missing_or_no_samples_does_not_zero(self):
  cfg={'prometheus':{'url':'https://prom.example.invalid','freshness_expression':'up == 1','queries':{'worker':'worker'}}}
  out=a.Collector(cfg,lambda *args:{'status':'success','data':{'resultType':'vector','result':[]}}).collect(NOW)
  self.assertEqual(out['ai'],{});self.assertIsNone(out['summary']['open'])
 def test_api_uses_only_configured_get_items(self):
  calls=[]
  def fetch(url,body,token):calls.append((url,body,token));return {'result':[item(1,10)]}
  with patch.dict(os.environ,{'NEXUS_ZABBIX_TOKEN':'test-token'}):a.Collector(CFG,fetch).collect(NOW)
  self.assertEqual(calls[0][1]['method'],'item.get');self.assertEqual(calls[0][1]['params']['itemids'],['1','2','3','4','5'])
 def test_prometheus_queries_share_the_snapshot_evaluation_clock(self):
  seen=[]
  def fetch(url,*args):seen.append(url);return {'status':'success','data':{'resultType':'vector','result':[{'value':[NOW,'1']}]}}
  cfg={'prometheus':{'url':'https://prom.example.invalid','freshness_expression':'up == 1','queries':{'worker':'worker'}}}
  x=a.Collector(cfg,fetch).collect(NOW);self.assertEqual(x['ai']['worker'],1);self.assertIn('time='+str(NOW),seen[0])
 def test_read_only_routes_and_bearer(self):
  c=a.Collector({});c.collect();server=ThreadingHTTPServer(('127.0.0.1',0),a.make_handler(c,'reader-secret'));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(server.server_port)
  try:
   for path in ['/snapshot','/snapshot?url=https://example.invalid','/config']:
    with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(url+path)
    self.assertEqual(e.exception.code,401 if path=='/snapshot' else 404)
   with urllib.request.urlopen(urllib.request.Request(url+'/snapshot',headers={'Authorization':'Bearer reader-secret'})) as r:self.assertEqual(r.status,200)
   with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(urllib.request.Request(url+'/snapshot',data=b'{}',method='POST'))
   self.assertEqual(e.exception.code,405)
  finally:server.shutdown();server.server_close();thread.join()
 def test_configuration_bounds(self):
  with self.assertRaises(ValueError):a.Collector({'servers':[{'id':'a','items':{'cpu_percent':'not-an-id'}}]})
  with self.assertRaises(ValueError):a.Collector({'servers':[{'id':'duplicate'},{'id':'duplicate'}]})
if __name__=='__main__':unittest.main()
