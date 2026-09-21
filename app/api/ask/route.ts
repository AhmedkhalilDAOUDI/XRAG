import {z} from 'zod';
import {owner,json,failure,checkOrigin,rateLimit,HttpError} from '@/lib/runtime';
import {ask} from '@/lib/workflow';
export async function POST(r:Request){try{checkOrigin(r);const u=owner(r);await rateLimit(u,'ask',12);if(Number(r.headers.get('content-length'))>10000)throw new HttpError(413,'Question is too long.');const p=z.object({question:z.string().trim().min(3).max(2000),mode:z.enum(['hybrid','vector','lexical','graph']).default('hybrid')}).safeParse(await r.json());if(!p.success)throw new HttpError(400,'Enter a question between 3 and 2,000 characters.');return json(await ask(u,p.data.question,p.data.mode));}catch(e){return failure(e);}}
