import fs from 'node:fs/promises';
import path from 'node:path';
const base=process.env.N6_BASE_URL||'http://localhost:5173';
const signin=await fetch(`${base}/signin-with-chatgpt?return_to=/`,{redirect:'manual'});
const cookie=signin.headers.get('set-cookie')?.split(';')[0];
if(!cookie)throw new Error('Local sign-in failed. This test is for the local preview.');
const headers={Cookie:cookie};
const manifest=JSON.parse(await fs.readFile('../DETAILS/test-data/manifest.json','utf8'));
const results={time:new Date().toISOString(),base,scope:'Kaggle local engineering integration; no enterprise quality claims',checks:[],documents:[]};
async function call(route,options={}){const r=await fetch(`${base}${route}`,{...options,headers:{...headers,...options.headers}});const text=await r.text();let data;try{data=JSON.parse(text);}catch{data={error:text};}return{status:r.status,data};}
function check(name,ok,details){results.checks.push({name,passed:!!ok,...(details?{details}:{})});console.log(name,ok?'PASS':'FAIL');if(!ok)throw new Error(name);}
try{
 const unauth=await fetch(`${base}/api/documents`);check('Unauthenticated API denied',unauth.status===401);
 const health=await call('/api/health');check('Database and model configured',health.status===200&&health.data.modelConfigured);
 const origin=await call('/api/ask',{method:'POST',headers:{Origin:'https://attacker.invalid','Content-Type':'application/json'},body:JSON.stringify({question:'Test question'})});check('Cross-origin mutation denied',origin.status===403);
 for(const d of manifest.documents){const text=await fs.readFile(path.join('../DETAILS/test-data',d.filename),'utf8'),form=new FormData();form.set('file',new File([text],d.filename,{type:'text/plain'}));form.set('pages',JSON.stringify([{page:null,text}]));form.set('title',d.title);form.set('extraction','Kaggle testing UTF-8 text');const started=Date.now(),r=await call('/api/documents',{method:'POST',body:form});check(`Import ${d.filename}`,r.status===201,r.data);results.documents.push({...r.data,filename:d.filename,milliseconds:Date.now()-started});}
 const docs=await call('/api/documents');check('Documents persisted',docs.data.documents.length===4);
 const d=manifest.documents[0],text=await fs.readFile(path.join('../DETAILS/test-data',d.filename),'utf8'),form=new FormData();form.set('file',new File([text],d.filename,{type:'text/plain'}));form.set('pages',JSON.stringify([{page:null,text}]));const duplicate=await call('/api/documents',{method:'POST',body:form});check('SHA-256 deduplication',duplicate.data.duplicate===true);
 const graph=await call('/api/graph');results.graph={entities:graph.data.entities.length,edges:graph.data.edges.length};check('Graph contains extracted entities',graph.data.entities.length>0);check('Relations retain exact source quotes',graph.data.edges.every(e=>e.quote.length>=12&&e.chunk_id&&e.document_id));
 const question="What businesses does Alphabet operate and how is Google related to it?";
 for(const mode of ['lexical','vector','graph','hybrid']){const r=await call('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question,mode})});check(`Question pipeline ${mode}`,r.status===200,r.status===200?{sources:r.data.sources.length,abstained:r.data.abstained,durationMs:r.data.durationMs}:r.data);if(r.status===200){await fs.writeFile(`../DETAILS/test-data/answer-${mode}.json`,JSON.stringify(r.data,null,2));check(`Citation mapping ${mode}`,[...r.data.answer.matchAll(/\[(S\d+)\]/g)].every(m=>r.data.sources.some(s=>s.citation===m[1])));}}
 const r=await call('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:'What is the exact colour of the fictional moon cheese recipe approved in 2099?',mode:'hybrid'})});check('Insufficient-evidence abstention',r.status===200&&r.data.abstained===true);
 const exportResult=await call('/api/export');check('Graph export with provenance',exportResult.status===200&&exportResult.data.format==='n6-graph-v1');await fs.writeFile('../DETAILS/test-data/graph-export.json',JSON.stringify(exportResult.data));
 const history=await call('/api/history');check('Question history persisted',history.data.history.length>=5);
 const dl=await fetch(`${base}/api/documents/${docs.data.documents[0].id}?download=1`,{headers});check('Original download bytes preserved',dl.status===200&&(await dl.text()).length>100);
 const invalid=await call('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"question":"a"}'});check('Invalid question rejected',invalid.status===400);
}finally{await fs.writeFile('../DETAILS/integration-results.json',JSON.stringify(results,null,2));}
