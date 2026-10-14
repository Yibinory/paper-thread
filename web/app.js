'use strict';
const $ = s => document.querySelector(s);
const escapeHTML = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const bundle = window.READER_BUNDLE || {documents:{},revisions:{},reader:{}};
const live = /^https?:$/.test(location.protocol);
const root = $('#main');
let docs = Object.values(bundle.documents).filter(d=>d.status==='ready' && !d.redirect);
let reader = {...bundle.reader};
try { reader = {...reader,...JSON.parse(localStorage.getItem('paper-reader-state') || '{}')}; } catch {}
let currentDoc = null, filter = '', searchTimer, searchSequence = 0, routeSequence = 0;
let drawerStack = [], drawerOrigin = null, observer;
const stateNames = {unread:'未读',reading:'阅读中',known:'已掌握',confused:'还不懂',done:'已读完'};
const asset = path => location.protocol==='file:' && path.startsWith('/') ? path.slice(1) : path;
const encodedPDF = path => '/' + path.split('/').map(encodeURIComponent).join('/');
const routeURL = d => '#/' + d.kind + '/' + d.id;
const toast = text => { $('#toast').textContent=text; $('#toast').hidden=false; clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').hidden=true,3500); };
async function api(path, data) {
  const result=await fetch('/api/'+path, data ? {method:'POST',headers:{'Content-Type':'application/json','X-Paper-Reader':'1'},body:JSON.stringify(data)} : {});
  const body=await result.json();if(!result.ok)throw Error(body.error || result.statusText);return body;
}
async function getDoc(id, revision) {
  if(live) return api('document?id='+encodeURIComponent(id)+(revision?'&revision='+revision:''));
  let d=revision ? bundle.revisions[id+'@'+revision] : bundle.documents[id];
  if(!d && bundle.documents[id]?.revision===revision)d=bundle.documents[id];
  if(!d)throw Error('找不到这份内容：'+id);
  const seen=new Set();
  while(d.redirect && !revision){if(seen.has(d.id))throw Error('重定向循环');seen.add(d.id);d=bundle.documents[d.redirect];}
  return {...d,latest_revision:bundle.documents[d.id]?.revision,backlinks:backlinks(id)};
}
function backlinks(id) {
  return docs.filter(d=>d.sections?.some(s=>s.html.includes('data-concept="'+id+'"'))).map(d=>({id:d.id,title:d.title,kind:d.kind}));
}
async function saveReader(id, change) {
  const previous=reader[id] || {state:'unread',note:''};
  try {
    if(live)reader=await api('reader',{id,...change});
    else {reader[id]={...previous,...change,updated:Date.now()/1000};localStorage.setItem('paper-reader-state',JSON.stringify(reader));}
    document.querySelectorAll('[data-state][data-id="'+id+'"]').forEach(b=>{const selected=reader[id]?.state===b.dataset.state;b.classList.toggle('selected',selected);b.setAttribute('aria-pressed',String(selected));});
    toast('已保存');
  } catch(e){toast('保存失败：'+e.message);}
}
function controls(doc) {
  const states=doc.kind==='concept'?['known','confused','unread']:['reading','done','unread'];
  const selected=reader[doc.id]?.state || 'unread';
  return '<div class="article-controls"><div class="reading-state" role="group" aria-label="阅读状态"><span class="controls-label">标记</span>'+states.map(s=>`<button data-id="${doc.id}" data-state="${s}" aria-pressed="${selected===s}" class="${selected===s?'selected':''}">${stateNames[s]}</button>`).join('')+'</div>'+(doc.kind==='report'?'<button class="print-button" data-print>打印 / 保存 PDF ↗</button>':'')+'</div>';
}
function sectionHTML(doc) {
  return doc.sections.map((s,i)=>`<section id="${s.id}"><span class="section-number">${String(i+1).padStart(2,'0')}</span><h2>${escapeHTML(s.title)}</h2>${s.html}</section>`).join('');
}
function referencesHTML(doc) {
  return `<div class="sources"><h3>来源与核查</h3><ol>${doc.sources.map(s=>`<li><a href="${escapeHTML(asset(s.url))}" target="_blank" rel="noopener">${escapeHTML(s.title)}</a>${s.locator?' · '+escapeHTML(s.locator):''}</li>`).join('')}</ol>${doc.paper?.coverage?`<p class="coverage">材料范围：${escapeHTML(doc.paper.coverage)}</p>`:''}<p class="coverage">关键概念可点击展开，引用可回到原文核查。</p></div>`;
}
function notesHTML(doc) {
  return `<section class="notes-area"><h2>阅读笔记</h2><p class="hint">${live?'笔记保存在本地知识库。':'离线包的笔记保存在当前浏览器。'}</p><label class="sr-only" for="note-${doc.id}">阅读笔记</label><textarea id="note-${doc.id}" placeholder="记录问题或想法…">${escapeHTML(reader[doc.id]?.note || '')}</textarea><button data-save-note="${doc.id}">保存笔记</button></section>`;
}
function pageHeader(doc,compact=false) {
  let info='';
  if(doc.paper){
    const p=doc.paper;
    info=`<p class="paper-title">${escapeHTML(p.title)}</p><div class="meta-row"><span>${escapeHTML(Array.isArray(p.authors)?p.authors.join(' · '):p.authors)}</span><span>${escapeHTML(p.venue)} · ${p.year}</span><span>约 ${doc.reading_minutes || 25} 分钟</span><a target="_blank" rel="noopener" href="${asset(encodedPDF(p.pdf))}">打开原文 ↗</a></div>`;
  } else info=`<div class="meta-row"><span>${escapeHTML(doc.aliases?.join(' · ') || '')}</span></div>`;
  return `<header class="article-head"><span class="eyebrow">${escapeHTML(doc.domain)}<span class="eyebrow-separator">/</span>${doc.kind==='report'?'论文报告':'知识介绍'}</span><h1>${escapeHTML(doc.title)}</h1>${doc.subtitle?`<p class="paper-title">${escapeHTML(doc.subtitle)}</p>`:''}<p class="lead">${escapeHTML(doc.summary)}</p>${info}${controls(doc)}</header>`;
}
function renderShelf(kind='report') {
  const isReport=kind==='report';
  document.title=(isReport?'论文库':'知识库')+' · 文脉';
  currentDoc=null;
  const collection=docs.filter(d=>d.kind===kind);
  // Broader shelves organize tutorials without changing their scientific domains.
  const knowledgeGroups={
    '数学与统计':['概率基础','概率与统计','概率与信息','数学与优化','评价方法'],
    '学习与生成':['深度学习','机器学习','模型训练','生成模型'],
    '因果推断':['因果推断'],
    '检索与计算系统':['向量检索','计算系统','计算机系统'],
    '软件工程':['软件工程']
  };
  const shelfDomain=d=>isReport?d.domain:Object.keys(knowledgeGroups).find(k=>knowledgeGroups[k].includes(d.domain)) || d.domain;
  const presentDomains=new Set(collection.map(shelfDomain));
  const domains=isReport?[...presentDomains]:[...Object.keys(knowledgeGroups).filter(k=>presentDomains.has(k)),...presentDomains].filter((d,i,a)=>a.indexOf(d)===i);
  root.innerHTML=`<div class="shelf ${isReport?'report-shelf':'knowledge-shelf'}"><header class="shelf-head"><div><h1>${isReport?'论文':'知识'}<span class="collection-count">${collection.length}</span></h1><p class="intro">${isReport?'阅读报告与原始论文':'独立的知识介绍，在需要时查阅。'}</p></div><span class="shelf-index">${isReport?'阅读目录':'按领域收录'}</span></header><div class="filterbar"><div class="domain-filters" role="group" aria-label="按领域筛选"><button class="active" data-filter="" aria-pressed="true">全部</button>${domains.map(d=>`<button data-filter="${escapeHTML(d)}" aria-pressed="false">${escapeHTML(d)}</button>`).join('')}</div><label class="shelf-search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg><input id="shelf-filter" aria-label="筛选当前书架" placeholder="${isReport?'查找论文':'名称、别名或关键词'}" type="search"></label></div><div class="collection-caption"><span id="result-count" role="status"></span><span>${isReport?'年份':'概念与应用'}</span></div><div id="cards" class="${isReport?'paper-list':'knowledge-groups'}"></div><footer class="footline"><span>文脉 · 个人阅读库</span><span>正文、知识与笔记保存在本机</span></footer></div>`;
  filter='';
  const render=()=>{
    const q=$('#shelf-filter').value.trim().toLowerCase();
    const visible=collection.filter(d=>(!filter || shelfDomain(d)===filter) && [d.title,d.subtitle,d.summary,d.domain,...d.tags||[],...d.aliases||[]].join(' ').toLowerCase().includes(q));
    $('#result-count').textContent=(q||filter?'找到 ':'共 ')+visible.length+(isReport?' 篇论文':' 篇知识介绍');
    const row=d=>`<a class="paper-row" href="${routeURL(d)}"><span class="row-number" aria-hidden="true">${String(collection.indexOf(d)+1).padStart(2,'0')}</span><div class="row-body"><h2>${escapeHTML(d.title)}</h2><p class="description">${escapeHTML(d.summary)}</p><div class="row-meta"><span>${escapeHTML(d.domain)}</span><span>${d.reading_minutes || 25} 分钟${reader[d.id]?.state && reader[d.id].state!=='unread'?'</span><span class="reader-mark">'+stateNames[reader[d.id].state]:''}</span></div></div><div class="row-end"><span>${d.paper?.year || '—'}</span><span class="row-arrow" aria-hidden="true">↗</span></div></a>`;
    const concept=d=>`<a class="concept-entry" href="${routeURL(d)}"><h3>${escapeHTML(d.title)}<span aria-hidden="true">↗</span></h3><p>${escapeHTML(d.summary)}</p><div class="aliases">${escapeHTML((d.aliases||[]).slice(0,3).join(' / '))}${reader[d.id]?.state==='known'?' · 已掌握':''}</div></a>`;
    $('#cards').innerHTML=(isReport?visible.map(row).join(''):domains.map(domain=>{const entries=visible.filter(d=>shelfDomain(d)===domain);return entries.length?`<section class="knowledge-group"><header><h2>${escapeHTML(domain)}</h2><span>${entries.length}</span></header><div class="concept-entries">${entries.map(concept).join('')}</div></section>`:'';}).join('')) || (collection.length ? '<div class="empty"><p>没有找到匹配的内容</p><span>试试另一种叫法，或调整领域筛选。</span></div>' : `<div class="empty"><p>${isReport?'还没有论文报告':'还没有知识介绍'}</p><span>${isReport?'请按项目 README 安装 skills，让 Agent 阅读第一篇论文。完成后刷新这里。':'阅读论文时，Agent 会按需补充知识；你也可以单独请求一份知识教程。'}</span></div>`);
  };
  $('#shelf-filter').addEventListener('input',render);
  root.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{filter=b.dataset.filter;root.querySelectorAll('[data-filter]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});render();});render();
}
function conceptFooter(doc) {
  return `${doc.not_this?.length?`<div class="sources"><h3>注意区分</h3><ul>${doc.not_this.map(t=>`<li>${escapeHTML(t)}</li>`).join('')}</ul></div>`:''}${doc.backlinks?.length?`<div class="sources"><h3>在这些内容中使用</h3><div class="related">${doc.backlinks.map(d=>`<a href="#/${d.kind}/${d.id}" data-close-drawer>${escapeHTML(d.title)}</a>`).join('')}</div></div>`:''}${live?`<details class="sources"><summary>补充这个知识的叫法</summary><p>确认指向同一概念后添加；有歧义的缩写请写明领域。</p><form class="alias-form" data-alias-id="${doc.id}" data-revision="${doc.latest_revision||doc.revision}"><input required maxlength="160" aria-label="新的别名" placeholder="中文名、英文名或带领域的缩写"><button>添加</button></form></details>`:''}`;
}
async function renderDocument(id, section, seq) {
  const doc=await getDoc(id);
  if(seq!==routeSequence)return;
  currentDoc=doc;
  document.title=doc.title+' · 文脉';
  const tocLinks=doc.sections.map((s,i)=>`<a class="section-link" href="#/${doc.kind}/${doc.id}/${s.id}" data-scroll="${s.id}"><span class="toc-number">${String(i+1).padStart(2,'0')}</span><span>${escapeHTML(s.title)}</span></a>`).join('');
  const back=`<a class="back-link" href="#/${doc.kind==='report'?'library':'knowledge'}">← ${doc.kind==='report'?'论文库':'知识库'}</a>`;
  root.innerHTML=`<div class="page-shell"><aside class="toc">${back}<p class="toc-label">本文目录 <span>${doc.sections.length} 节</span></p><nav aria-label="文章目录">${tocLinks}</nav></aside><article class="article"><div class="mobile-reading-nav">${back}<details class="mobile-toc"><summary>目录 <span aria-hidden="true">⌄</span></summary><nav aria-label="移动端文章目录">${tocLinks}</nav></details></div>${pageHeader(doc)}<div class="prose">${sectionHTML(doc)}</div>${doc.kind==='concept'?conceptFooter(doc):''}${referencesHTML(doc)}${notesHTML(doc)}</article></div>`;
  hydrate(root,doc);
  observer?.disconnect();
  observer=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting){root.querySelectorAll('.section-link').forEach(a=>a.classList.toggle('active',a.dataset.scroll===e.target.id));}}},{rootMargin:'-100px 0px -65% 0px'});
  root.querySelectorAll('.prose>section').forEach(s=>observer.observe(s));
  if(section)requestAnimationFrame(()=>root.querySelector('#'+CSS.escape(section))?.scrollIntoView());
}
function hydrate(container,doc) {
  container.querySelectorAll('a[data-concept]').forEach(a=>{
    const id=a.dataset.concept;
    a.href='#/concept/'+id+(a.dataset.section?'/'+a.dataset.section:'');
    a.title='展开知识介绍';
    a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey)return;e.preventDefault();openConcept(id,a.dataset.section,doc.references?.[id]);});
  });
  container.querySelectorAll('a[data-source]').forEach(a=>{
    let url=a.dataset.source==='paper' && doc.paper? encodedPDF(doc.paper.pdf):doc.sources.find(s=>s.id===a.dataset.source)?.url;
    if(url){if(a.dataset.page)url=url.split('#')[0]+'#page='+a.dataset.page;a.href=asset(url);a.target='_blank';a.rel='noopener';}
  });
  container.querySelectorAll('img').forEach(img=>{img.src=asset(img.getAttribute('src'));img.loading='lazy';img.onclick=()=>{const dialog=document.createElement('dialog');dialog.className='image-dialog';const close=document.createElement('button');close.textContent='关闭';close.onclick=()=>{dialog.close();dialog.remove();};const image=img.cloneNode();image.removeAttribute('loading');dialog.append(close,image);document.body.append(dialog);dialog.showModal();dialog.addEventListener('close',()=>dialog.remove());};});
  container.querySelectorAll('[data-demo]').forEach(renderDemo);
  container.querySelectorAll('[data-interactive]').forEach(host=>window.PaperInteractions?.render(host,doc.interactives?.[host.dataset.interactive]));
  if(window.renderMathInElement)renderMathInElement(container,{delimiters:[{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false},{left:'$$',right:'$$',display:true}],throwOnError:false,strict:false,trust:false});
  container.querySelectorAll('[data-state]').forEach(b=>b.onclick=()=>saveReader(b.dataset.id,{state:b.dataset.state}));
  container.querySelectorAll('[data-print]').forEach(b=>b.onclick=()=>window.print());
  container.querySelectorAll('[data-save-note]').forEach(b=>b.onclick=()=>saveReader(b.dataset.saveNote,{note:container.querySelector('#note-'+b.dataset.saveNote).value}));
  container.querySelectorAll('[data-scroll]').forEach(a=>a.onclick=e=>{e.preventDefault();a.closest('.mobile-toc')?.removeAttribute('open');container.querySelector('#'+CSS.escape(a.dataset.scroll))?.scrollIntoView({behavior:'auto'});history.replaceState(null,'','#/'+doc.kind+'/'+doc.id+'/'+a.dataset.scroll);});
  container.querySelectorAll('[data-close-drawer]').forEach(a=>a.onclick=closeDrawer);
  container.querySelectorAll('.alias-form').forEach(form=>form.onsubmit=async e=>{e.preventDefault();try{await api('alias',{id:form.dataset.aliasId,alias:form.querySelector('input').value,expected_revision:form.dataset.revision});toast('别名已添加，现在可以用这个叫法搜索。');form.querySelector('input').value='';const latest=await getDoc(form.dataset.aliasId);form.dataset.revision=latest.revision;}catch(e){toast(e.message);}});
}
async function openConcept(id,section,revision,push=true) {
  if($('#drawer').hidden){drawerOrigin=document.activeElement;drawerStack=[];}
  try {
    const doc=await getDoc(id,revision);
    if(revision && currentDoc?.kind==='report')doc.references=currentDoc.references;
    if(push)drawerStack.push({id,section,revision});
    $('#drawer').hidden=false;$('#drawer-backdrop').hidden=false;
    $('#drawer-back').hidden=drawerStack.length<2;
    const changed=doc.latest_revision && doc.latest_revision!==doc.revision;
    $('#drawer-body').innerHTML=`<span class="eyebrow">${escapeHTML(doc.domain)}</span><h1>${escapeHTML(doc.title)}</h1><p class="lead">${escapeHTML(doc.summary)}</p><a class="full-link" href="#/concept/${doc.id}${section?'/'+section:''}" data-close-drawer>打开完整知识页 ↗</a>${changed?'<div class="version-note">当前显示报告引用时的知识版本。完整知识页提供最新修订。</div>':''}${controls(doc)}<div class="prose">${sectionHTML(doc)}</div>${conceptFooter(doc)}${referencesHTML(doc)}${notesHTML(doc)}`;
    hydrate($('#drawer-body'),doc);
    $('#drawer').scrollTop=0;
    if(section){const target=$('#drawer-body').querySelector('#'+CSS.escape(section));if(target)$('#drawer').scrollTop=target.offsetTop-80;}
    $('#drawer-close').focus({preventScroll:true});
  }catch(e){toast(e.message);}
}
function closeDrawer(){ $('#drawer').hidden=true;$('#drawer-backdrop').hidden=true;drawerStack=[];drawerOrigin?.focus({preventScroll:true}); }
$('#drawer-close').onclick=closeDrawer;$('#drawer-backdrop').onclick=closeDrawer;
$('#drawer-back').onclick=()=>{drawerStack.pop();const t=drawerStack.at(-1);if(t)openConcept(t.id,t.section,t.revision,false);};
function renderNotes(){document.title='阅读笔记 · 文脉';currentDoc=null;const items=docs.filter(d=>reader[d.id]?.note || ['known','confused','done','reading'].includes(reader[d.id]?.state));root.innerHTML=`<div class="shelf"><header class="shelf-head"><div><h1>阅读笔记<span class="collection-count">${items.length}</span></h1><p class="intro">保存的想法与阅读标记。</p></div></header><div class="article-controls"><button id="notes-export">导出笔记备份</button><button id="notes-import">导入备份（保留现有笔记）</button><input type="file" id="notes-file" accept="application/json,.json" hidden></div>${items.map(d=>`<div class="note-card"><span class="domain-label">${stateNames[reader[d.id].state]||'笔记'}</span><h2><a href="${routeURL(d)}">${escapeHTML(d.title)} ↗</a></h2><p>${escapeHTML(reader[d.id].note)}</p></div>`).join('')||'<p class="empty">还没有笔记。在报告或知识页底部写下第一条想法。</p>'}</div>`;
  $('#notes-export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,reader},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='paper-reader-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  $('#notes-import').onclick=()=>$('#notes-file').click();
  $('#notes-file').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>3000000)throw Error('备份过大');const data=JSON.parse(await file.text());if(data.version!==1||!data.reader||typeof data.reader!=='object')throw Error('不是有效的笔记备份');let imported=0,skipped=0;const entries=Object.entries(data.reader);for(const [id,note] of entries){if(!docs.some(d=>d.id===id)||!note||!stateNames[note.state]||typeof note.note!=='string'||note.note.length>50000){skipped++;continue;}const old=reader[id];if(old&&(old.note||old.state!=='unread')){skipped++;continue;}if(live)reader=await api('reader',{id,state:note.state,note:note.note});else reader[id]={...note,updated:Date.now()/1000};imported++;}if(!live)localStorage.setItem('paper-reader-state',JSON.stringify(reader));renderNotes();toast(`已导入 ${imported} 条；保留或跳过 ${skipped} 条。`);}catch(err){toast('导入失败：'+err.message);}};
}
async function route(){
  closeDrawer();
  const seq=++routeSequence;
  let [kind,id,section,legacySection]=location.hash.slice(2).split('/');
  if(kind==='compare'){
    kind='report';section=legacySection;
    history.replaceState(null,'','#/report/'+id+(section?'/'+section:''));
  }
  document.querySelectorAll('.topbar nav a').forEach(a=>a.classList.toggle('active',a.id==='nav-'+(kind==='report'?'library':kind==='concept'?'knowledge':kind||'library')));
  window.scrollTo(0,0);
  try{
    if(kind==='report'||kind==='concept')await renderDocument(id,section,seq);
    else if(kind==='knowledge')renderShelf('concept');
    else if(kind==='notes')renderNotes();
    else renderShelf();
  }catch(e){root.innerHTML=`<div class="empty"><h1>暂时无法打开</h1><p>${escapeHTML(e.message)}</p><a href="#/library">返回书架</a></div>`;}
}
function offlineSearch(q,kind){const tokens=q.toLowerCase().split(/\s+/);return docs.filter(d=>!kind||d.kind===kind).map(d=>{const text=[d.title,...d.aliases||[],d.summary,...d.semantic_terms||[]].join(' ').toLowerCase();return {...d,score:tokens.reduce((n,t)=>n+(text.includes(t)?1:0),0)};}).filter(d=>d.score).sort((a,b)=>b.score-a.score).slice(0,10);}
async function search(){const seq=++searchSequence;const q=$('#search-input').value.trim(),kind=$('#search-kind').value;if(!q){$('#search-results').innerHTML='<p class="empty">可以搜索中文名、英文名、别名或关键词。</p>';return;}$('#search-results').innerHTML='<p class="empty">正在查找相关内容…</p>';try{const response=live?await api('search?q='+encodeURIComponent(q)+'&kind='+kind):{results:offlineSearch(q,kind),retrieval:'lexical'};if(seq!==searchSequence)return;$('#search-results').innerHTML=response.results.map(d=>`<a class="search-result" href="#/${d.kind}/${d.id}"><h3>${escapeHTML(d.title)}</h3><p>${escapeHTML(d.summary)}</p><p>${escapeHTML(d.domain)} · ${d.kind==='concept'?'知识':'论文'}${d.aliases?.length?' · '+escapeHTML(d.aliases.slice(0,3).join(' / ')):''}</p></a>`).join('')||'<p class="empty">没有找到。可以试试另一种叫法，或描述它的作用。</p>';$('#search-results').insertAdjacentHTML('beforeend',`<p class="search-note">名称、别名与关键词查找。 相似内容可能属于不同概念，请结合定义阅读。</p>`);$('#search-results').querySelectorAll('a').forEach(a=>a.onclick=()=>$('#search-dialog').close());}catch(e){$('#search-results').innerHTML=`<p class="empty">${escapeHTML(e.message)}</p>`;}}
function launchSearch(){$('#search-dialog').showModal();$('#search-input').focus();}
$('#search-input').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();search();}};$('#search-kind').onchange=search;$('#search-launch').onclick=launchSearch;$('#search-input').oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(search,300);};
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();launchSearch();}if(e.key==='Escape'&&!$('#drawer').hidden)closeDrawer();if(e.key==='Tab'&&!$('#drawer').hidden){const f=[...$('#drawer').querySelectorAll('a[href],button:not([hidden]),input,textarea,summary')].filter(n=>n.offsetParent!==null);const first=f[0],last=f.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}});
try{document.body.classList.toggle('dark',localStorage.getItem('paper-reader-theme')==='dark');}catch{}
$('#theme').onclick=()=>{document.body.classList.toggle('dark');try{localStorage.setItem('paper-reader-theme',document.body.classList.contains('dark')?'dark':'light');}catch{}};
window.addEventListener('hashchange',route);
$('#search-launch kbd').textContent=/Mac|iPhone|iPad/.test(navigator.platform)?'⌘ K':'Ctrl K';

function renderDemo(host){
  const name=host.dataset.demo;host.classList.add('demo');
  const head='<div class="demo-label">可操作的教学示例 · 非论文实验复现</div>';
  if(name==='bounds'){
    host.innerHTML=head+'<label>维度 D：<b class="value">128</b><input type="range" min="4" max="9" value="7" step="1" aria-label="向量维度"></label><div class="demo-bars"></div><div class="demo-output"></div>';
    const update=()=>{const D=2**Number(host.querySelector('input').value);host.querySelector('.value').textContent=D;let seed=42;const rnd=()=>{seed=(1664525*seed+1013904223)>>>0;return(seed+1)/4294967297;};const normal=()=>Math.sqrt(-2*Math.log(rnd()))*Math.cos(2*Math.PI*rnd());let errors=[];for(let r=0;r<240;r++){let o=Array.from({length:D},normal);let norm=Math.hypot(...o);o=o.map(x=>x/norm);let e=Array.from({length:D},normal);let dot=e.reduce((s,x,i)=>s+x*o[i],0);e=e.map((x,i)=>x-dot*o[i]);norm=Math.hypot(...e);e=e.map(x=>x/norm);let denom=0,num=0;for(let i=0;i<D;i++){const b=Math.sign(o[i])/Math.sqrt(D);denom+=b*o[i];num+=b*(.6*o[i]+.8*e[i]);}errors.push(num/denom-.6);}const bins=Array(16).fill(0);errors.forEach(x=>bins[Math.max(0,Math.min(15,Math.floor((x+.4)/.8*16)))]++);const max=Math.max(...bins);host.querySelector('.demo-bars').innerHTML=bins.map(n=>`<div class="demo-bar" style="height:${Math.max(2,100*n/max)}%"></div>`).join('');host.querySelector('.demo-output').textContent=`固定真实内积 0.6，采样 240 组随机正交方向。估计误差均值 ${(errors.reduce((a,b)=>a+b,0)/240).toFixed(4)}，平均绝对误差 ${(errors.reduce((a,b)=>a+Math.abs(b),0)/240).toFixed(4)}。柱图横轴为误差 −0.4 至 0.4（超界计入端点）。维度增大时，观察误差如何集中；这组有限采样不能代替概率证明。`;};host.querySelector('input').oninput=update;update();
  }else if(name==='pq'){
    host.innerHTML=head+'<p>二维子向量各自编码：数据库向量 x=(0.8,0.2 | 0.1,0.9)，两个码本都含 (1,0) 与 (0,1)。编码得到 (0,1)。</p><label>查询第一个坐标：<b class="value">0.5</b><input type="range" min="0" max="100" value="50" aria-label="查询坐标"></label><div class="demo-output"></div>';
    const update=()=>{const a=+host.querySelector('input').value/100;host.querySelector('.value').textContent=a.toFixed(2);const q=[a,.5,.2,.8],x=[.8,.2,.1,.9],xhat=[1,0,0,1];const exact=q.reduce((s,v,i)=>s+(v-x[i])**2,0),approx=q.reduce((s,v,i)=>s+(v-xhat[i])**2,0);host.querySelector('.demo-output').innerHTML=`查询 q=(${a.toFixed(2)},0.5 | 0.2,0.8)<br>第一张表查到 ${((a-1)**2+.25).toFixed(3)}，第二张表查到 0.080，累加得到 PQ 距离 ${approx.toFixed(3)}。<br>原始向量的平方距离为 ${exact.toFixed(3)}。注意：编码不变，查询变化时重建查找表。`;};host.querySelector('input').oninput=update;update();
  }else if(name==='minimax'){
    host.innerHTML=head+'<p>用一个标量变换强度 a 演示：模型损失设为 a，失真惩罚设为 λa²。增强阶段在 [0,1] 内最大化 a−λa²。</p><label>惩罚权重 λ：<b class="value">1.00</b><input type="range" min="0" max="300" value="100" aria-label="失真惩罚权重"></label><div class="demo-flow"><span class="demo-node">原样本</span>→<span class="demo-node on">选择增强强度</span>→<span class="demo-node">训练模型</span></div><div class="demo-output"></div>';
    const update=()=>{const l=+host.querySelector('input').value/100,a=l?Math.min(1,1/(2*l)):1;host.querySelector('.value').textContent=l.toFixed(2);host.querySelector('.demo-output').textContent=`最优强度 a=${a.toFixed(3)}，损失项=${a.toFixed(3)}，加权失真=${(l*a*a).toFixed(3)}。增大 λ 会限制增强强度。本示例只解释最大化阶段的权衡，不表示 AdvST 的实际图像损失曲线。`;};host.querySelector('input').oninput=update;update();
  }else if(name==='causal'){
    host.innerHTML=head+'<p>构造机制 X=2P+U。已观察到 P=1、X=5，因此反推出 U=3。干预 P 时保留这个 U。</p><label>干预后的 P：<b class="value">2</b><input type="range" min="0" max="4" value="2" step=".1" aria-label="干预值"></label><div class="demo-flow"><span class="demo-node">反推 U=3</span>→<span class="demo-node on">修改 P</span>→<span class="demo-node">重新计算 X</span></div><div class="demo-output"></div>';
    const update=()=>{const p=+host.querySelector('input').value;host.querySelector('.value').textContent=p.toFixed(1);host.querySelector('.demo-output').textContent=`在指定机制下，X反事实=2×${p.toFixed(1)}+3=${(2*p+3).toFixed(1)}。这里固定个体状态 U；如果重新随机抽取 U，得到的是另一种生成过程。机制本身是否正确，需要额外依据。`;};host.querySelector('input').oninput=update;update();
  }else if(name==='graph'){
    const steps=['用户报告输出错误，先定位公开接口。','读取接口调用的组合函数，提出中间状态被改写的假设。','沿调用依赖检查辅助函数，把假设对应到具体代码。','输出需要核查或修改的候选集合；后续仍需测试验证。'];let step=0;
    host.innerHTML=head+'<div class="demo-flow">'+['问题描述','接口函数','组合函数','辅助函数'].map((s,i)=>`<span class="demo-node" data-node="${i}">${s}</span>`).join(' → ')+'</div><div class="demo-output"></div><button class="prev">← 上一步</button> <button class="next">下一步 →</button>';
    const update=()=>{host.querySelectorAll('[data-node]').forEach(n=>n.classList.toggle('on',+n.dataset.node<=step));host.querySelector('.demo-output').textContent=(step+1)+' / 4 · '+steps[step];host.querySelector('.prev').disabled=step===0;host.querySelector('.next').disabled=step===3;};host.querySelector('.prev').onclick=()=>{step--;update();};host.querySelector('.next').onclick=()=>{step++;update();};update();
  }else host.innerHTML=head+'<p>此演示暂不可用，请阅读正文的完整例子。</p>';
}
(async()=>{if(live){try{const data=await api('catalog');docs=data.documents;reader=data.reader;}catch(e){toast('本地服务暂不可用，显示已保存的内容。');}}await route();})();
