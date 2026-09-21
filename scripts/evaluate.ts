/** Small document-retrieval benchmark. Gold labels were written before ranking. */
import fs from 'node:fs/promises';
import {performance} from 'node:perf_hooks';
import {retrieve} from '../lib/core';
import type {Mode} from '../lib/types';
const config=Object.fromEntries((await fs.readFile('.dev.vars','utf8')).trim().split('\n').filter(x=>x.includes('=')).map(x=>[x.slice(0,x.indexOf('=')),x.slice(x.indexOf('=')+1)]));
const corpus=JSON.parse(await fs.readFile('../DETAILS/test-data/graph-export.json','utf8'));
const gold=[
 {q:'How does Alphabet describe the relationship between Google and its other businesses?',f:['kaggle-test-1.txt']},
 {q:'Which company provides Google Maps and Android?',f:['kaggle-test-1.txt']},
 {q:'What are the four operating segments of Merck?',f:['kaggle-test-2.txt']},
 {q:'Which company supplies animal vaccines to veterinarians and animal producers?',f:['kaggle-test-2.txt']},
 {q:'How does Pfizer generate most of its revenue?',f:['kaggle-test-3.txt']},
 {q:'Which pharmaceutical company was incorporated in Delaware on June 2, 1942?',f:['kaggle-test-3.txt']},
 {q:'How does Microsoft connect intelligent cloud and intelligent edge?',f:['kaggle-test-4.txt']},
 {q:'Which technology company describes voice, ink, and gaze interactions?',f:['kaggle-test-4.txt']},
 {q:'How do Merck and Pfizer describe their medicines and vaccines businesses?',f:['kaggle-test-2.txt','kaggle-test-3.txt']},
 {q:'Compare the descriptions of technology and access in Alphabet and Microsoft.',f:['kaggle-test-1.txt','kaggle-test-4.txt']}
];
await fs.writeFile('../DETAILS/test-data/gold-questions.json',JSON.stringify({method:'Manually authored from four source texts before first ranking run; no independent human review',questions:gold},null,2));
async function embed(texts:string[],input_type:string){const vectors:number[][]=[];for(let i=0;i<texts.length;i+=16){const r=await fetch('https://integrate.api.nvidia.com/v1/embeddings',{method:'POST',headers:{Authorization:`Bearer ${config.NVIDIA_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify({model:config.NVIDIA_EMBED_MODEL,input:texts.slice(i,i+16),input_type,truncate:'END'})});if(!r.ok)throw new Error(`Embedding status ${r.status}`);const d:any=await r.json();vectors.push(...d.data.sort((a:any,b:any)=>a.index-b.index).map((x:any)=>x.embedding));}return vectors;}
const [cv,qv]=await Promise.all([embed(corpus.chunks.map((c:any)=>c.text),'passage'),embed(gold.map(g=>g.q),'query')]);corpus.chunks.forEach((c:any,i:number)=>c.vector=cv[i]);
const manifest=JSON.parse(await fs.readFile('../DETAILS/test-data/manifest.json','utf8')),fileIds=new Map(manifest.documents.map((d:any)=>[d.filename,corpus.chunks.find((c:any)=>c.title===d.title)?.document_id]));
const summary:any={time:new Date().toISOString(),model:config.NVIDIA_EMBED_MODEL,documents:manifest.documents.length,passages:corpus.chunks.length,questions:gold.length,label_author:'AI-authored, source-checked, not independently reviewed',k:3,measurement:'Document-level retrieval only; ranking latency excludes model/network/storage',modes:{}};
for(const mode of ['lexical','vector','graph','hybrid'] as Mode[]){const runs=gold.map((g,i)=>{const start=performance.now(),r=retrieve(g.q,mode,corpus.chunks,qv[i],corpus.entities,corpus.edges,corpus.mentions),latency=performance.now()-start,ranked=[...new Set(r.sources.map(s=>s.document_id))].slice(0,3),expected=g.f.map(f=>fileIds.get(f)),hits=ranked.filter(id=>expected.includes(id)).length,first=ranked.findIndex(id=>expected.includes(id));return{question:i+1,recallAt3:hits/expected.length,precisionAt3:hits/3,rr:first<0?0:1/(first+1),milliseconds:latency};});summary.modes[mode]={recallAt3:runs.reduce((s,r)=>s+r.recallAt3,0)/runs.length,precisionAt3:runs.reduce((s,r)=>s+r.precisionAt3,0)/runs.length,mrr:runs.reduce((s,r)=>s+r.rr,0)/runs.length,meanRankingMs:runs.reduce((s,r)=>s+r.milliseconds,0)/runs.length};await fs.writeFile(`../DETAILS/test-data/ranking-${mode}.json`,JSON.stringify(runs,null,2));}
await fs.writeFile('../DETAILS/evaluation-results.json',JSON.stringify(summary,null,2));console.log(JSON.stringify(summary,null,2));
