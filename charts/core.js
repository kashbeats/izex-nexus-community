// IZEX NEXUS — MIT. Community edition: live observations or explicitly labelled synthetic fixture.
const C={bg:'#080f1e',panel:'#0d1b2c',line:'#23374b',text:'#edf6ff',muted:'#91a6bc',teal:'#46ebc0',blue:'#52b9ff',purple:'#b29cff',amber:'#ffcd70',red:'#ff7189',unknown:'#8493a8'};
const W=context.panel.chart.getWidth(), H=context.panel.chart.getHeight();
const frames=context.panel.data.series||[];
let now=Date.now()/1000;
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const fresh=(t,ttl=180)=>finite(t)&&now-t>=0&&now-t<=ttl;
function field(frame,name){return Array.from(frame?.fields.find(f=>f.name===name)?.values||[]);}
let S={};try{const raw=frames.flatMap(f=>field(f,'snapshot'))[0];S=raw?JSON.parse(raw):{};if(!S.checked_at){const observed=frames.map(f=>f.meta?.custom?.data).find(d=>d&&typeof d==='object'&&finite(d.checked_at));if(observed)S=observed;}}catch(e){}
if(context.panel.data.state==='Error')S={};
if(NEXUS_DEMO){S=NEXUS_FIXTURE;now=1767225600;} // Fixed fixture clock, never enabled by upstream content.
const live=S.stale===false&&fresh(S.checked_at,120);
const sourceCurrent=(name)=>live&&S.coverage?.[name]?.ok===true&&S.coverage?.[name]?.complete===true;
const m=(s,k)=>{const a=s?.metrics?.[k];return sourceCurrent('zabbix')&&fresh(a?.checked_at)&&finite(a?.value)?a.value:null;};
const pct=(a,b)=>finite(a)&&finite(b)&&a>=0&&b>0&&a<=b?100*a/b:null;
const color=v=>!finite(v)?C.unknown:v>=90?C.red:v>=75?C.amber:C.teal;
const fmt=v=>finite(v)?v.toFixed(1):'—';
const age=t=>!finite(t)||t<=0||now<t?'UNKNOWN':now-t<3600?Math.floor((now-t)/60)+'m':now-t<86400?Math.floor((now-t)/3600)+'h':Math.floor((now-t)/86400)+'d';
const g=[];
function text(x,y,value,size=12,fill=C.text,extra={}){g.push({type:'text',silent:true,x,y,style:{text:String(value),font:`${size>=20?600:400} ${size}px monospace`,fill,...extra}});}
function rect(x,y,w,h,fill=C.panel,stroke=C.line,r=9){g.push({type:'rect',silent:true,shape:{x,y,width:w,height:h,r},style:{fill,stroke,lineWidth:1}});}
function line(x1,y1,x2,y2,stroke=C.line,dash=false){g.push({type:'line',silent:true,shape:{x1,y1,x2,y2},style:{stroke,lineWidth:1,lineDash:dash?[4,5]:undefined}});}
function base(extra={}){if(NEXUS_DEMO)text(W-12,12,'SYNTHETIC DEMO',9,C.amber,{textAlign:'right'});return {backgroundColor:C.bg,animation:false,aria:{enabled:true},graphic:g,...extra};}
function unknown(note='Waiting for current evidence'){text(24,34,'EVIDENCE UNAVAILABLE',20,C.unknown);text(24,68,note,12,C.muted);return base();}
const servers=(Array.isArray(S.servers?.servers)?S.servers.servers:[]).slice(0,5);
