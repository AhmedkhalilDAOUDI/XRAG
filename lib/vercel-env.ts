// Vercel stand-in for `cloudflare:workers`: next.config.ts aliases that import here, so lib/ keeps its D1/R2 calls.
// DB speaks the D1 subset XRAG uses (prepare/bind/all/first/run/batch) over libSQL (Turso); FILES speaks the R2 subset over private Vercel Blob.
import {createClient,type Client,type ResultSet} from '@libsql/client';
import {put,get,del} from '@vercel/blob';
let client:Client|undefined;
const db=()=>client??=createClient({url:process.env.TURSO_DATABASE_URL||'',authToken:process.env.TURSO_AUTH_TOKEN});
const objects=(r:ResultSet)=>r.rows.map(row=>Object.fromEntries(r.columns.map((c,i)=>[c,row[i]])));
class Statement{
 constructor(readonly sql:string,readonly args:unknown[]=[]){}
 bind(...args:unknown[]){return new Statement(this.sql,args);}
 private exec(){return db().execute({sql:this.sql,args:this.args as never});}
 async all<T>(){return{results:objects(await this.exec()) as T[]};}
 async first<T>(){return((await this.all<T>()).results[0]??null) as T|null;}
 async run(){await this.exec();return{success:true};}
}
const DB={
 prepare:(sql:string)=>new Statement(sql),
 // One libSQL write transaction, matching D1's all-or-nothing batch.
 batch:async(statements:Statement[])=>(await db().batch(statements.map(s=>({sql:s.sql,args:s.args as never})),'write')).map(r=>({results:objects(r)})),
};
const FILES={
 put:(key:string,bytes:ArrayBuffer,options?:{httpMetadata?:{contentType?:string}})=>put(key,Buffer.from(bytes),{access:'private',contentType:options?.httpMetadata?.contentType,addRandomSuffix:false,allowOverwrite:true}),
 get:async(key:string)=>{const r=await get(key,{access:'private'});return r?.statusCode===200&&r.stream?{body:r.stream}:null;},
 delete:(key:string)=>del(key),
};
// SINGLE_OWNER: no gateway strips identity headers here, so owner() must never trust them, even when APP_PASSWORD is missing.
export const env={...process.env,DB,FILES,SINGLE_OWNER:true};
