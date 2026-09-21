import {owner,json,failure} from '@/lib/runtime';
import {loadCorpus} from '@/lib/ingestion';
export async function GET(r:Request){try{const corpus=await loadCorpus(owner(r));return json({format:'n6-graph-v1',exported_at:new Date().toISOString(),...corpus,chunks:corpus.chunks.map(c=>({...c,vector:undefined}))});}catch(e){return failure(e);}}
