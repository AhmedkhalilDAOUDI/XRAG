import {test} from 'node:test';
import assert from 'node:assert/strict';
import {extractPassages,ExtractionValidationError} from '../lib/extraction';
const batch=[{id:'p1',text:'Example Company develops software.'}];
const valid=JSON.stringify({passages:[{id:'p1',entities:[{name:'Example Company',kind:'Organization'}],relations:[]}]});
test('Malformed JSON or invalid schema is regenerated once from original input',async()=>{
 for(const invalid of ['{bad',valid.replace('Organization','Corporation')]){
  let calls=0;const result=await extractPassages(batch,async(system,user)=>{assert.equal(user,JSON.stringify(batch));calls++;if(calls===2)assert.match(system,/Previous response/);return calls===1?invalid:valid;});
  assert.equal(calls,2);assert.equal(result[0].entities[0].kind,'Organization');
 }
});
test('Repeated malformed output fails closed after two calls',async()=>{
 let calls=0;await assert.rejects(extractPassages(batch,async()=>{calls++;return '{bad';}),ExtractionValidationError);assert.equal(calls,2);
});
test('Unknown or missing passage identifiers are never accepted',async()=>{
 for(const invalid of [valid.replace('p1','unknown'),'{"passages":[]}'])await assert.rejects(extractPassages(batch,async()=>invalid),ExtractionValidationError);
});
test('Provider failures propagate without schema retries',async()=>{
 let calls=0;const error=new Error('provider unavailable');await assert.rejects(extractPassages(batch,async()=>{calls++;throw error;}),e=>e===error);assert.equal(calls,1);
});
