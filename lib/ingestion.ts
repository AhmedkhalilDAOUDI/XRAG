import {extractPassages,ExtractionValidationError} from './extraction';
import {chunkPages,normalized,MAX_CHARACTERS,MAX_CORPUS_CHUNKS} from './core';
import {runtime,rows,digest,HttpError} from './runtime';
import {chat,embed,modelIds} from './nvidia';
import type {Chunk,Page} from './types';
export async function ingest(user:string,file:File,pages:Page[],title:string,extraction:string){
 if(file.size>8*1024*1024)throw new HttpError(413,'Files must be smaller than 8 MB.');
 const characters=pages.reduce((s,p)=>s+p.text.length,0);if(characters<40)throw new HttpError(422,'No usable text found. Enable OCR for scanned documents.');if(characters>MAX_CHARACTERS)throw new HttpError(413,'Document text exceeds 40,000 characters. Split it into smaller files.');
 const bytes=await file.arrayBuffer(),sha=await digest(bytes),existing=await rows<{id:string}>('SELECT id FROM documents WHERE owner=? AND sha=?',user,sha);if(existing.length)return{id:existing[0].id,duplicate:true};
 const id=crypto.randomUUID(),chunks=chunkPages(pages,id),count=await rows<{n:number}>('SELECT COUNT(*) n FROM chunks WHERE owner=?',user);if((count[0]?.n||0)+chunks.length>MAX_CORPUS_CHUNKS)throw new HttpError(413,'Workspace capacity is 500 passages. Remove documents before importing more.');
 const vectors=await embed(chunks.map(c=>c.text),'passage');chunks.forEach((c,i)=>c.vector=vectors[i]);
 const extracted:Awaited<ReturnType<typeof extractPassages>>=[];
 for(let i=0;i<chunks.length;i+=4){
  try{extracted.push(...await extractPassages(chunks.slice(i,i+4).map(c=>({id:c.id,text:c.text})),(system,user)=>chat(system,user,3500)));}
  catch(error){if(error instanceof ExtractionValidationError)throw new HttpError(502,error.message);throw error;}
 }
 const db=runtime().DB,storageKey=`${await digest(user)}/${id}`,now=new Date().toISOString(),statements:D1PreparedStatement[]=[db.prepare('INSERT INTO documents (id,owner,title,filename,mime,sha,storage_key,status,chunks,characters,embedding_model,created_at,extraction) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)').bind(id,user,title,file.name,file.type||'application/octet-stream',sha,storageKey,'ready',chunks.length,characters,modelIds().embedding,now,extraction)];
 for(const c of chunks)statements.push(db.prepare('INSERT INTO chunks (id,owner,document_id,ordinal,page,section,text,vector) VALUES (?,?,?,?,?,?,?,?)').bind(c.id,user,id,c.ordinal,c.page,c.section,c.text,JSON.stringify(c.vector)));
 let relationCount=0;const used=new Set<string>();
 for(const p of extracted){const chunk=chunks.find(c=>c.id===p.id);if(!chunk)continue;const entityMap=new Map<string,string>();
  for(const e of p.entities){const name=normalized(e.name);if(!name||!normalized(chunk.text).includes(name))continue;const eid=(await digest(`${user}:${e.kind}:${name}`)).slice(0,32);entityMap.set(name,eid);
   if(!used.has(eid)){statements.push(db.prepare('INSERT OR IGNORE INTO entities (id,owner,label,kind) VALUES (?,?,?,?)').bind(eid,user,e.name,e.kind));used.add(eid);}
   statements.push(db.prepare('INSERT OR IGNORE INTO mentions (id,owner,entity_id,chunk_id) VALUES (?,?,?,?)').bind(`${eid}:${chunk.id}`,user,eid,chunk.id));
  }
  for(const r of p.relations){const source=entityMap.get(normalized(r.source)),target=entityMap.get(normalized(r.target)),quote=normalized(r.quote);if(!source||!target||source===target||!normalized(chunk.text).includes(quote)||!quote.includes(normalized(r.source))||!quote.includes(normalized(r.target)))continue;const relation=r.relation.toUpperCase().replace(/[^A-Z0-9_]/g,'_');const eid=await digest(`${chunk.id}:${source}:${relation}:${target}`);statements.push(db.prepare('INSERT OR IGNORE INTO edges (id,owner,source,target,relation,quote,chunk_id) VALUES (?,?,?,?,?,?,?)').bind(eid,user,source,target,relation,r.quote,chunk.id));relationCount++;}
 }
 if(statements.length>950)throw new HttpError(413,'This document contains too many graph facts. Split it into smaller files.');
 await runtime().FILES.put(storageKey,bytes,{httpMetadata:{contentType:file.type||'application/octet-stream'}});
 try{await db.batch(statements);}catch(error){await runtime().FILES.delete(storageKey);const duplicate=await rows<{id:string}>('SELECT id FROM documents WHERE owner=? AND sha=?',user,sha);if(duplicate.length)return{id:duplicate[0].id,duplicate:true};throw error;}
 return{id,duplicate:false,chunks:chunks.length,entities:used.size,relations:relationCount};
}
export async function loadCorpus(user:string){
 const [stored,entities,edges,mentions]=await Promise.all([rows<Omit<Chunk,'vector'>&{vector:string}>('SELECT c.*,d.title FROM chunks c JOIN documents d ON d.id=c.document_id WHERE c.owner=? AND d.status=?',user,'ready'),rows<any>('SELECT id,label,kind FROM entities WHERE owner=?',user),rows<any>('SELECT id,source,target,relation,quote,chunk_id FROM edges WHERE owner=?',user),rows<{entity_id:string;chunk_id:string}>('SELECT entity_id,chunk_id FROM mentions WHERE owner=?',user)]);
 return{chunks:stored.map(c=>({...c,vector:JSON.parse(c.vector) as number[]})),entities,edges,mentions};
}
