if(!live)return unknown();
text(20,14,'01 / EVIDENCE CONSTELLATION',11,C.blue);text(20,35,'CPU % / UTILIZATION COLORS · DECLARED LINKS, NOT TRAFFIC',9,C.muted);
const cx=W*.5,cy=H*.44,R=Math.min(W*.30,H*.25),pos={};
for(const r of [R*.56,R,R*1.16])g.push({type:'circle',silent:true,shape:{cx,cy,r},style:{fill:'none',stroke:C.line,lineWidth:1,lineDash:[3,7]}});
servers.forEach((s,i)=>{const a=(-90+i*360/Math.max(1,servers.length))*Math.PI/180;pos[s.id]=[cx+R*Math.cos(a),cy+R*Math.sin(a)];});
for(const [a,b] of (S.topology?.links||[]).slice(0,24)){if(pos[a]&&pos[b])line(...pos[a],...pos[b],'#34526d',true);}
for(const s of servers){const [x,y]=pos[s.id],cpu=m(s,'cpu_percent'),co=color(cpu);g.push({type:'circle',silent:true,shape:{cx:x,cy:y,r:30},style:{fill:C.panel,stroke:co,lineWidth:2,shadowBlur:finite(cpu)?10:0,shadowColor:co}});text(x,y-7,finite(cpu)?fmt(cpu)+'%':'—',15,co,{textAlign:'center'});text(x+(x<cx-50?-18:0),y+42,String(s.name||s.id),9,C.text,{textAlign:'center',width:130,overflow:'truncate'});}
rect(cx-66,cy-29,132,58,'#102638',C.blue,14);text(cx,cy-16,'IZEX NEXUS',16,C.text,{textAlign:'center'});text(cx,cy+9,NEXUS_DEMO?'SYNTHETIC DATA':'SNAPSHOT CURRENT',9,NEXUS_DEMO?C.amber:C.teal,{textAlign:'center'});
const feeds=Object.entries(S.coverage||{}).slice(0,5),bw=(W-40)/Math.max(1,feeds.length);
feeds.forEach(([n,v],i)=>{const x=20+i*bw,ok=v.ok&&v.complete;rect(x,H-77,bw-7,38,C.panel,ok?C.teal:C.amber,5);text(x+8,H-69,n.toUpperCase(),9,C.muted);text(x+8,H-54,ok?'CURRENT':'GAP',10,ok?C.teal:C.amber);});
text(20,H-22,'Relationships are configured. This is not automatic discovery or traffic analysis.',9,C.muted);return base();
