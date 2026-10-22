const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const charts=path.join(__dirname,'../charts'),core=fs.readFileSync(path.join(charts,'core.js'),'utf8');
function run(name,s,mode=false){const c={panel:{chart:{getWidth:()=>900,getHeight:()=>420},data:{series:[{fields:[],meta:{custom:{data:s}}}]}}};return new Function('context',`const NEXUS_DEMO=${mode};const NEXUS_FIXTURE=${JSON.stringify(s)};\n`+core+'\n'+fs.readFileSync(path.join(charts,name+'.js'),'utf8'))(c);}
const past={checked_at:1767225600,stale:false,coverage:{zabbix:{ok:true,complete:true}},servers:{servers:[]}};
test('demo has a fixed clock and visibly labels synthetic data',()=>{const o=run('header',past,true);assert.ok(JSON.stringify(o).includes('SYNTHETIC DEMO'));assert.ok(JSON.stringify(o).includes('DEMO / FICTIONAL DATA'));});
test('live cannot be switched to demo by upstream data',()=>{const o=run('fleet',{...past,demo:true},false);assert.ok(JSON.stringify(o).includes('EVIDENCE UNAVAILABLE'));});
test('unconfigured incident feed does not claim zero incidents',()=>{const o=run('incidents',{checked_at:Date.now()/1000,stale:false,summary:{open:null}},false);assert.ok(JSON.stringify(o).includes('Incident feed is not configured'));});
test('all charts handle absent observations',()=>{for(const n of ['header','fleet','constellation','business','ai','recovery','storage','incidents'])assert.ok(run(n,{}));});
