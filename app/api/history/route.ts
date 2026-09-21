import {owner,json,failure,rows,checkOrigin,runtime} from '@/lib/runtime';
export async function GET(r:Request){try{const u=owner(r);return json({history:(await rows<{response:string}>('SELECT response FROM queries WHERE owner=? ORDER BY created_at DESC LIMIT 30',u)).map(x=>JSON.parse(x.response))});}catch(e){return failure(e);}}
export async function DELETE(r:Request){try{checkOrigin(r);const u=owner(r);await runtime().DB.prepare('DELETE FROM queries WHERE owner=?').bind(u).run();return json({deleted:true});}catch(e){return failure(e);}}
