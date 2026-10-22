if(!live)return unknown();
text(18,14,'05 / INCIDENT FLIGHT RECORDER',11,C.blue);
const rows=(S.incidents||[]).filter(r=>!r.test).slice(0,5),rh=Math.min(68,(H-76)/Math.max(1,rows.length));
if(!rows.length){text(24,65,S.summary?.open==null?'Incident feed is not configured.':'No recorded non-test incidents.',16,S.summary?.open==null?C.unknown:C.teal);}
rows.forEach((r,i)=>{const y=45+i*rh,co=r.status==='resolved'?C.teal:r.status==='unknown'?C.unknown:C.amber;line(23,y+4,23,y+rh,C.line);g.push({type:'circle',silent:true,shape:{cx:23,cy:y+12,r:4},style:{fill:co}});text(39,y+3,(r.status||'unknown').toUpperCase()+' / '+(r.severity||'observation'),10,co);text(39,y+22,r.title||r.id,12,C.text,{width:W-65,overflow:'truncate'});text(39,y+41,String(r.id),8,C.muted);});
text(18,H-20,'Observe → diagnose → recover → verify. Controlled test rows excluded.',9,C.muted);
return base();
