import type {Page} from './types';
export async function parseFile(file:File,ocr:boolean,progress:(s:string)=>void):Promise<{pages:Page[];method:string}>{
 if(file.size>8*1024*1024)throw new Error('Files must be smaller than 8 MB.');
 const ext=file.name.split('.').pop()?.toLowerCase();
 if(ext==='pdf'){
  const pdfjs=await import('pdfjs-dist');pdfjs.GlobalWorkerOptions.workerSrc='/pdf.worker.min.mjs';
  const task=pdfjs.getDocument({data:new Uint8Array(await file.arrayBuffer()),useSystemFonts:true});const pdf=await task.promise;
  if(pdf.numPages>100){await task.destroy();throw new Error('PDFs are limited to 100 pages. Split this file first.');}
  const pages:Page[]=[];let worker:any=null,usedOCR=false,total=0;
  try{for(let n=1;n<=pdf.numPages;n++){progress(`Reading page ${n} of ${pdf.numPages}`);const page=await pdf.getPage(n),content=await page.getTextContent();let text=content.items.map((i:any)=>i.str||'').join(' ');
   if(text.trim().length<40&&ocr){if(!worker){const {createWorker}=await import('tesseract.js');worker=await createWorker('eng');}progress(`Recognising text on page ${n} of ${pdf.numPages}`);const viewport=page.getViewport({scale:1.5}),canvas=document.createElement('canvas');canvas.width=viewport.width;canvas.height=viewport.height;await page.render({canvas,canvasContext:canvas.getContext('2d')!,viewport}).promise;text=(await worker.recognize(canvas)).data.text;usedOCR=true;canvas.width=canvas.height=0;}
   total+=text.length;if(total>40000)throw new Error('Document text exceeds 40,000 characters. Split the file first.');pages.push({page:n,text});page.cleanup();
  }}finally{if(worker)await worker.terminate();await task.destroy();}
  return{pages,method:usedOCR?'PDF.js + Tesseract English OCR':'PDF.js text extraction'};
 }
 if(ext==='docx'){const mammoth=await import('mammoth/mammoth.browser');const result=await mammoth.extractRawText({arrayBuffer:await file.arrayBuffer()});return{pages:[{page:null,text:result.value}],method:'Mammoth DOCX text extraction'};}
 if(!['txt','md','csv','json'].includes(ext||''))throw new Error('Use a PDF, DOCX, TXT, Markdown, CSV or JSON file.');
 return{pages:[{page:null,text:await file.text()}],method:'UTF-8 text extraction'};
}
