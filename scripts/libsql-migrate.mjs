// Applies drizzle/*.sql to the libSQL (Turso) database named by TURSO_DATABASE_URL, once each, in order.
// Uses the same d1_migrations table name as Wrangler. Each file and its record commit in one transaction.
import fs from 'node:fs/promises';
import {createClient} from '@libsql/client';
if(!process.env.TURSO_DATABASE_URL)throw new Error('TURSO_DATABASE_URL is not set.');
const db=createClient({url:process.env.TURSO_DATABASE_URL,authToken:process.env.TURSO_AUTH_TOKEN});
await db.execute('CREATE TABLE IF NOT EXISTS d1_migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)');
const applied=new Set((await db.execute('SELECT name FROM d1_migrations')).rows.map(r=>r.name));
for(const name of (await fs.readdir('drizzle')).filter(f=>f.endsWith('.sql')).sort()){
 if(applied.has(name))continue;
 const statements=(await fs.readFile(`drizzle/${name}`,'utf8')).split('--> statement-breakpoint').map(s=>s.trim()).filter(Boolean);
 await db.batch([...statements,{sql:'INSERT INTO d1_migrations (name) VALUES (?)',args:[name]}],'write');
 console.log('applied',name);
}
console.log('migrations up to date');
