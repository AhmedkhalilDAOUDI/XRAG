"""Import an authenticated N6 graph export into a scoped Neo4j mirror.
Usage: python scripts/neo4j_import.py /path/to/export.json
Requires NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD. Never deletes other data.
"""
import json, os, sys
from neo4j import GraphDatabase
payload=json.load(open(sys.argv[1]))
if payload.get('format')!='n6-graph-v1': raise SystemExit('Not an N6 export')
uri=os.environ.get('NEO4J_URI','bolt://127.0.0.1:7687')
driver=GraphDatabase.driver(uri,auth=(os.environ.get('NEO4J_USER','neo4j'),os.environ['NEO4J_PASSWORD']))
with driver.session() as session:
 session.run('CREATE CONSTRAINT n6_entity_id IF NOT EXISTS FOR (n:N6Entity) REQUIRE n.id IS UNIQUE').consume()
 session.run('CREATE CONSTRAINT n6_chunk_id IF NOT EXISTS FOR (n:N6Chunk) REQUIRE n.id IS UNIQUE').consume()
 def ingest(tx):
  tx.run('UNWIND $items AS item MERGE (n:N6Entity {id:item.id}) SET n.label=item.label,n.kind=item.kind',items=payload['entities']).consume()
  tx.run('UNWIND $items AS item MERGE (n:N6Chunk {id:item.id}) SET n.text=item.text,n.documentId=item.document_id,n.page=item.page,n.section=item.section,n.title=item.title',items=payload['chunks']).consume()
  tx.run('UNWIND $items AS item MATCH (a:N6Entity {id:item.source}),(b:N6Entity {id:item.target}),(c:N6Chunk {id:item.chunk_id}) MERGE (a)-[r:N6_RELATION {id:item.id}]->(b) SET r.predicate=item.relation,r.quote=item.quote,r.chunkId=item.chunk_id',items=payload['edges']).consume()
  tx.run('UNWIND $items AS item MATCH (a:N6Entity {id:item.entity_id}),(c:N6Chunk {id:item.chunk_id}) MERGE (a)-[:MENTIONED_IN]->(c)',items=payload['mentions']).consume()
 session.execute_write(ingest)
 print(json.dumps({'entities':len(payload['entities']),'relations':len(payload['edges']),'chunks':len(payload['chunks'])}))
driver.close()
