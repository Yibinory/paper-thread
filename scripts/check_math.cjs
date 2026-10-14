const fs=require('fs');const path=require('path');
const root=path.resolve(__dirname,'..');
const katex=require(path.join(root,'web/vendor/katex/katex.js'));
const decode=s=>s.replace(/&(#x[0-9a-f]+|#\d+|lt|gt|amp|quot|apos);/gi,(_,x)=>x[0]==='#'?String.fromCodePoint(x[1].toLowerCase()==='x'?parseInt(x.slice(2),16):parseInt(x.slice(1),10)):({lt:'<',gt:'>',amp:'&',quot:'"',apos:"'"})[x.toLowerCase()]);
let errors=[], count=0;
const directories=process.argv.slice(2).length?process.argv.slice(2).map(p=>path.resolve(p)):['concepts','reports'].map(t=>path.join(root,'data',t));
for(const directory of directories)for(const name of fs.readdirSync(directory)){
 if(!name.endsWith('.json'))continue;
 const doc=JSON.parse(fs.readFileSync(path.join(directory,name),'utf8'));
 for(const s of doc.sections||[]){
  for(const m of s.html.matchAll(/\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g)){
   count++;try{katex.renderToString(decode(m[1]||m[2]),{throwOnError:true,strict:false,trust:false});}catch(e){errors.push({doc:doc.id,section:s.id,formula:m[1]||m[2],error:e.message});}
  }
  if(/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(s.html))errors.push({doc:doc.id,section:s.id,error:'Unexpected control character; likely corrupted LaTeX escape'});
 }
}
console.log(JSON.stringify({formulas:count,errors},null,2));process.exitCode=errors.length?1:0;
