import type {Chunk,Page,Entity,Edge,Evidence,GraphPath,Mode} from './types';
export const MAX_CHARACTERS=40000,MAX_CHUNKS=64,MAX_CORPUS_CHUNKS=500;
const stop=new Set('a an and are as at be been by can did do does for from had has have how i in is it of on or our should that the their then there these they this to was were what when where which who why will with would you your'.split(' '));
export function tokens(s:string):string[]{return(s.toLowerCase().match(/[\p{L}\p{N}]+/gu)||[]).filter(w=>w.length>1&&!stop.has(w));}
export function normalized(s:string){return s.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();}
export function clean(s:string){return s.replace(/\r\n?/g,'\n').replace(/\u0000/g,'').replace(/[ \t]+/g,' ').replace(/\n{3,}/g,'\n\n').trim();}
export function chunkPages(pages:Page[],documentId:string):Chunk[]{
 const output:Chunk[]=[];let section='Document';
 for(const page of pages){const text=clean(page.text);let start=0;while(start<text.length){let end=Math.min(start+1100,text.length);if(end<text.length){const split=text.lastIndexOf(' ',end);if(split>start+700)end=split;}const body=text.slice(start,end).trim();const heading=body.match(/^#{1,4}\s+([^\n]+)/);if(heading)section=heading[1].slice(0,120);if(body.length>=20)output.push({id:`${documentId}:${output.length}`,document_id:documentId,ordinal:output.length,page:page.page,section,text:body,vector:[]});if(end===text.length)break;start=Math.max(start+1,end-140);}}
 if(output.length>MAX_CHUNKS)throw new Error(`Document exceeds ${MAX_CHUNKS} passages. Split the file first.`);return output;
}
export function cosine(a:number[],b:number[]){if(!a.length||a.length!==b.length)return 0;let dot=0,x=0,y=0;for(let i=0;i<a.length;i++){dot+=a[i]*b[i];x+=a[i]**2;y+=b[i]**2;}return x&&y?dot/Math.sqrt(x*y):0;}
export function lexicalRanks(question:string,chunks:Chunk[]){const qt=[...new Set(tokens(question))],docs=chunks.map(c=>tokens(c.text)),avg=docs.reduce((s,d)=>s+d.length,0)/(docs.length||1),df=new Map(qt.map(t=>[t,docs.filter(d=>d.includes(t)).length]));return chunks.map((c,i)=>({id:c.id,score:qt.reduce((s,t)=>{const f=docs[i].filter(x=>x===t).length,n=df.get(t)||0;return s+Math.log(1+(chunks.length-n+.5)/(n+.5))*(f*2.2)/(f+1.2*(.25+.75*docs[i].length/(avg||1)));},0)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));}
export function graphSearch(question:string,entities:Entity[],edges:Edge[],mentions:{entity_id:string;chunk_id:string}[]){
 const q=normalized(question),qt=new Set(tokens(question)),seeds=entities.filter(e=>q.includes(normalized(e.label))||tokens(e.label).filter(t=>qt.has(t)).length/Math.max(1,tokens(e.label).length)>=.75).slice(0,8),scores=new Map<string,number>(),paths:GraphPath[]=[];let frontier=seeds.map(e=>({entities:[e.id],edges:[] as Edge[]}));
 for(const seed of seeds)for(const m of mentions.filter(m=>m.entity_id===seed.id))scores.set(m.chunk_id,1);
 for(let depth=0;depth<2;depth++){const next:GraphPath[]=[];for(const path of frontier){const id=path.entities[path.entities.length-1];for(const edge of edges.filter(e=>e.source===id||e.target===id).slice(0,20)){const target=edge.source===id?edge.target:edge.source;if(path.entities.includes(target))continue;const p={entities:[...path.entities,target],edges:[...path.edges,edge]};next.push(p);paths.push(p);scores.set(edge.chunk_id,(scores.get(edge.chunk_id)||0)+1/(depth+1));for(const m of mentions.filter(m=>m.entity_id===target))scores.set(m.chunk_id,(scores.get(m.chunk_id)||0)+.4/(depth+1));}}frontier=next.slice(0,40);}
 return {ranked:[...scores].map(([id,score])=>({id,score})).sort((a,b)=>b.score-a.score),paths:paths.slice(0,24)};
}
export function retrieve(question:string,mode:Mode,chunks:Chunk[],queryVector:number[],entities:Entity[],edges:Edge[],mentions:{entity_id:string;chunk_id:string}[]){
 const graph=graphSearch(question,entities,edges,mentions),branches:Record<string,{id:string;score:number}[]>={lexical:lexicalRanks(question,chunks),vector:queryVector.length?chunks.map(c=>({id:c.id,score:cosine(queryVector,c.vector)})).filter(x=>x.score>.3).sort((a,b)=>b.score-a.score):[],graph:graph.ranked},use=mode==='hybrid'?['lexical','vector','graph']:[mode],fused=new Map<string,{score:number;branches:string[]}>();
 for(const branch of use)branches[branch].slice(0,30).forEach((c,i)=>{const v=fused.get(c.id)||{score:0,branches:[]};v.score+=1/(60+i+1);v.branches.push(branch);fused.set(c.id,v);});
 const byId=new Map(chunks.map(c=>[c.id,c])),selected:Evidence[]=[],perDoc=new Map<string,number>();for(const[id,v]of[...fused].sort((a,b)=>b[1].score-a[1].score)){const c=byId.get(id);if(!c||(perDoc.get(c.document_id)||0)>=3)continue;selected.push({...c,...v,citation:`S${selected.length+1}`});perDoc.set(c.document_id,(perDoc.get(c.document_id)||0)+1);if(selected.length===6)break;}
 return{sources:selected,paths:graph.paths.filter(p=>p.edges.every(e=>selected.some(s=>s.id===e.chunk_id))).slice(0,8)};
}
export function validateClaims(raw:unknown,sources:Evidence[]):{answer:string;abstained:boolean;rejected:number}{
 const data=raw as {claims?:{text?:unknown;citations?:unknown;quotes?:unknown}[]};let rejected=0;const claims=Array.isArray(data?.claims)?data.claims.slice(0,8):[],accepted:string[]=[];
 for(const claim of claims){if(typeof claim.text!=='string'||claim.text.length>1600||!Array.isArray(claim.citations)||!claim.citations.length||!Array.isArray(claim.quotes)||claim.quotes.length!==claim.citations.length){rejected++;continue;}const quotes=claim.quotes;
  if(claim.citations.some((id,i)=>typeof id!=='string'||!sources.some(s=>s.citation===id&&typeof quotes[i]==='string'&&quotes[i].trim().length>=12&&normalized(s.text).includes(normalized(quotes[i]))))){rejected++;continue;}const text=claim.text.replace(/\[S\d+\]/g,'').trim();if(text)accepted.push(`${text} ${[...new Set(claim.citations)].map(id=>`[${id}]`).join(' ')}`);}
 return{answer:accepted.length?accepted.join('\n\n'):'The indexed documents do not provide enough evidence to answer this question.',abstained:!accepted.length,rejected};
}
