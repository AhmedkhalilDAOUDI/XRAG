"""Poll a local directory and import new/changed files through the authenticated API.
Set N6_INGEST_URL=https://<your-site>/api/documents and N6_INGEST_TOKEN.
The production Sites private gate also requires an approved machine access path;
use this collector behind your trusted gateway, or local preview with --local.
Only .txt/.md/.csv/.json are parsed here; browser handles PDF/DOCX/OCR.
"""
import argparse, hashlib, json, os, pathlib, secrets, time, urllib.request, urllib.error
p=argparse.ArgumentParser();p.add_argument('directory',type=pathlib.Path);p.add_argument('--watch',type=int,default=0);p.add_argument('--local',action='store_true');a=p.parse_args()
url='http://localhost:5173/api/documents' if a.local else os.environ['N6_INGEST_URL']
headers={}
if a.local:
 import http.cookiejar
 opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));opener.open('http://localhost:5173/signin-with-chatgpt?return_to=/').close()
else:
 if not url.startswith('https://'):raise SystemExit('HTTPS required for credentials')
 headers['Authorization']='Bearer '+os.environ['N6_INGEST_TOKEN'];opener=urllib.request.build_opener()
seen={}
def run():
 for f in sorted(a.directory.iterdir()):
  if f.suffix.lower() not in ('.txt','.md','.csv','.json') or not f.is_file():continue
  data=f.read_bytes();sha=hashlib.sha256(data).hexdigest()
  if seen.get(str(f))==sha:continue
  text=data.decode('utf-8');boundary='n6'+secrets.token_hex(12);parts=[]
  for name,value in [('title',f.stem),('pages',json.dumps([{'page':None,'text':text}])),('extraction','Automated UTF-8 folder collector')]:parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
  safe=f.name.replace('"','_').replace('\n','_').replace('\r','_');parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{safe}"\r\nContent-Type: text/plain\r\n\r\n'.encode()+data+b'\r\n');parts.append(f'--{boundary}--\r\n'.encode())
  request=urllib.request.Request(url,data=b''.join(parts),headers={**headers,'Content-Type':'multipart/form-data; boundary='+boundary})
  try:
   with opener.open(request,timeout=240) as r: result=json.load(r)
   seen[str(f)]=sha;print(f.name,'duplicate' if result.get('duplicate') else 'indexed',flush=True)
  except urllib.error.HTTPError as e:print(f.name,'failed',e.code,flush=True)
run()
while a.watch:time.sleep(max(60,a.watch));run()
