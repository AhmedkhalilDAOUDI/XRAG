import {NextResponse,type NextRequest} from 'next/server';
import {runtime,passwordOk} from '@/lib/runtime';
// Prompts for the single-owner password on pages; API routes check it themselves in owner().
export function proxy(request:NextRequest){
 if(!runtime().APP_PASSWORD||passwordOk(request.headers.get('authorization')))return NextResponse.next();
 return new NextResponse('Authentication required.',{status:401,headers:{'WWW-Authenticate':'Basic realm="XRAG", charset="UTF-8"'}});
}
export const config={matcher:['/((?!api/|_next/|favicon.svg|pdf.worker).*)']};
