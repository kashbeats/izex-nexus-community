if(!live)return unknown('Snapshot missing, stale or future-dated. Historical values are withheld.');
if(!servers.length)return unknown('No configured server observations.');
const series=[],cw=W/servers.length;
servers.forEach((s,i)=>{
 const cpu=m(s,'cpu_percent'),ram=pct(m(s,'memory_used'),m(s,'memory_total')),x=i*cw;
 rect(x+5,5,cw-10,H-10);text(x+17,17,String(s.name||s.id),13,C.text,{width:cw-32,overflow:'truncate'});text(x+17,39,String(s.role||s.source||'CONFIGURED SOURCE'),9,C.muted,{width:cw-32,overflow:'truncate'});
 const radius=Math.min(cw*.27,(H-100)*.62),cy=H*.56;
 series.push({type:'gauge',center:[x+cw/2,cy],radius,startAngle:210,endAngle:-30,min:0,max:100,progress:{show:finite(cpu),width:8,itemStyle:{color:color(cpu)}},axisLine:{lineStyle:{width:8,color:[[1,C.line]]}},pointer:{show:false},axisTick:{show:false},splitLine:{show:false},axisLabel:{show:false},detail:{show:true,offsetCenter:[0,-2],formatter:finite(cpu)?fmt(cpu)+'%':'—',fontSize:Math.min(26,cw*.14),color:color(cpu)},title:{show:true,offsetCenter:[0,'48%'],fontSize:9,color:C.muted},data:[{value:cpu??0,name:finite(cpu)?'CPU UTILIZATION':'CPU UNKNOWN'}]});
 const by=H-47;line(x+17,by,x+cw-17,by);if(finite(ram))line(x+17,by,x+17+(cw-34)*ram/100,by,color(ram));text(x+17,by+10,'RAM '+fmt(ram)+(finite(ram)?'%':''),11,color(ram));text(x+17,H-19,'SOURCE SEMANTICS IN INVENTORY',8,C.muted);
});return base({series});
