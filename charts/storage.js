if(!sourceCurrent('zabbix'))return unknown();
text(18,14,'06 / CAPACITY PRESSURE',11,C.blue);text(18,35,'POOLS + FILESYSTEMS / NOT ADDITIVE',9,C.muted);
const rows=[];
for(const s of servers){for(const d of (s.disks||[]).slice(0,3))rows.push({name:s.name+' / '+d.name,value:fresh(d.checked_at)?pct(d.used,d.total):null});if(s.metrics?.disk_total)rows.push({name:s.name+' / FILESYSTEM',value:pct(m(s,'disk_used'),m(s,'disk_total'))});}
const shown=rows.slice(0,8),rh=Math.min(40,(H-100)/Math.max(1,shown.length));
shown.forEach((r,i)=>{const y=65+i*rh;text(20,y,r.name,10,C.text,{width:W*.65,overflow:'truncate'});text(W-22,y,fmt(r.value)+(finite(r.value)?'% USED':' UNKNOWN'),11,color(r.value),{textAlign:'right'});rect(20,y+19,W-42,6,C.line,C.line,3);if(finite(r.value))rect(20,y+19,(W-42)*r.value/100,6,color(r.value),color(r.value),3);});
text(20,H-24,'First 8 configured layers. Never sum overlapping pools, VMs or shared volumes.',9,C.muted);return base();
