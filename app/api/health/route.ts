import {owner,json,failure,runtime,rows} from '@/lib/runtime';
import {modelIds} from '@/lib/nvidia';
export async function GET(r:Request){try{owner(r);await rows('SELECT COUNT(*) FROM documents');return json({status:'ok',modelConfigured:!!runtime().NVIDIA_API_KEY,models:modelIds(),version:'1.0.0',limits:{charactersPerDocument:40000,bytesPerDocument:8388608,passagesPerWorkspace:500}});}catch(e){return failure(e);}}
