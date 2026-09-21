export type Page={page:number|null;text:string};
export type Chunk={id:string;document_id:string;ordinal:number;page:number|null;section:string;text:string;vector:number[];title?:string};
export type Entity={id:string;label:string;kind:string};
export type Edge={id:string;source:string;target:string;relation:string;quote:string;chunk_id:string};
export type Evidence=Chunk & {citation:string;score:number;branches:string[]};
export type GraphPath={entities:string[];edges:Edge[]};
export type Mode='hybrid'|'vector'|'lexical'|'graph';
export type Answer={id:string;question:string;answer:string;sources:Evidence[];paths:GraphPath[];mode:Mode;durationMs:number;warnings:string[];model:string;steps:string[];abstained:boolean;created_at:string};
