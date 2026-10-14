/* Trusted, data-driven paper explanations. No executable content in documents. */
(function(global){
'use strict';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fixed=(x,n=3)=>Number(x).toFixed(n);
function pqBound(values,m,delta,threshold){
  const bytes=values.map(v=>Math.min(127,Math.max(0,Math.floor((v-m)/delta+1e-12))));
  const sum=Math.min(127,bytes.reduce((a,b)=>a+b,0));
  const lower=values.length*m+delta*sum;
  return {bytes,sum,lower,exact:values.reduce((a,b)=>a+b,0),prune:lower>threshold+1e-10};
}
function rabitqBound(p,epsilon,budget,threshold){
  const E=Math.sqrt(1-p.a*p.a)/p.a*epsilon/Math.sqrt(p.dimension-1);
  const estimate=p.ro*p.ro+p.rq*p.rq-2*p.ro*p.rq*p.numerator/p.a;
  const radius=2*p.ro*p.rq*(E+budget),lower=estimate-radius;
  return {E,estimate,radius,lower,prune:lower>threshold};
}
function stepHTML(s){return `<h4>${esc(s.label)}</h4><p>${esc(s.caption)}</p><div class="state-grid">${s.states.map(x=>`<div class="state-cell ${esc(x.state)}"><span>${esc(x.label)}</span><b>${esc(x.value)}</b></div>`).join('')}</div><dl class="trace-explanation"><dt>本步改变</dt><dd>${esc(s.changes)}</dd><dt>保持不变</dt><dd>${esc(s.holds)}</dd><dt>为什么接着这样做</dt><dd>${esc(s.reason)}</dd></dl>`;}
function render(host,c){
  if(!c)return;
  const fallback=host.innerHTML;
  try{
    const panel=document.createElement('div');panel.className='interactive-ui';
    panel.innerHTML=`<div class="interactive-kicker">${esc(c.provenance)}</div><h3>${esc(c.title)}</h3><p class="interaction-question">${esc(c.question)}</p><div class="interaction-controls"></div><div class="interaction-body"></div><button class="interaction-reset" type="button">恢复初始状态</button>`;
    const controls=panel.querySelector('.interaction-controls'),body=panel.querySelector('.interaction-body');
    let reset;
    if(c.type==='trace'){
      let step=0;
      controls.innerHTML=`<div class="step-nav" role="group" aria-label="${esc(c.title)}步骤">${c.steps.map((s,i)=>`<button type="button" data-step="${i}" aria-pressed="${i===0}"><span>${i+1}</span>${esc(s.label)}</button>`).join('')}</div>`;
      const update=()=>{controls.querySelectorAll('[data-step]').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.step===step)));body.innerHTML=`<div class="trace-state" aria-live="polite" aria-atomic="true">${stepHTML(c.steps[step])}</div>`;};
      controls.querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>{step=+b.dataset.step;update();});reset=()=>{step=0;update();};
      const all=document.createElement('details');all.className='trace-all';all.innerHTML='<summary>展开全部状态的文字说明</summary>'+c.steps.map(stepHTML).join('');panel.append(all);
    } else if(c.type==='evidence'){
      controls.innerHTML=`<label>比较条件 <select aria-label="${esc(c.title)}的比较条件">${c.cases.map((s,i)=>`<option value="${i}">${esc(s.label)}</option>`).join('')}</select></label>`;
      const select=controls.querySelector('select');
      const update=()=>{const d=c.cases[+select.value];body.innerHTML=`<div aria-live="polite"><p class="evidence-condition">${esc(d.condition)}</p><table><caption>${esc(d.label)} · ${esc(c.measure)}</caption><thead><tr><th>方法 / 条件</th>${c.columns.map(x=>`<th>${esc(x)}</th>`).join('')}</tr></thead><tbody>${d.rows.map(r=>`<tr><th scope="row">${esc(r.label)}</th>${r.values.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table><p class="decision">${esc(d.takeaway)}</p></div>`;};
      select.onchange=update;reset=()=>{select.value='0';update();};
    } else if(c.type==='pq-bound'){
      controls.innerHTML='<label>当前第 k 名的 ADC 距离 τ <input type="range" min="2.5" max="4.5" step="0.1" value="3" aria-label="PQ 当前距离阈值"></label><label>字节量化步长 Δ <select aria-label="PQ 量化步长"><option value="0.2">0.2（粗）</option><option value="0.05">0.05（细）</option></select></label>';
      const input=controls.querySelector('input'),select=controls.querySelector('select');
      const update=()=>{const delta=+select.value,t=+input.value,r=pqBound(c.values,c.minimum,delta,t);body.innerHTML=`<div aria-live="polite"><div class="number-strip"><span>当前门槛<b>${fixed(t,1)}</b></span><span>保守下界 L<b>${fixed(r.lower,2)}</b></span><span>完整 ADC 距离<b>${fixed(r.exact,2)}</b></span></div><table><caption>8 次查表如何变成一个下界（平方距离单位）</caption><thead><tr><th>子空间</th>${c.values.map((_,i)=>`<th>${i+1}</th>`).join('')}</tr></thead><tbody><tr><th>小表值 v</th>${c.values.map(v=>`<td>${fixed(v,2)}</td>`).join('')}</tr><tr><th>向下取整 (v−0.1)/Δ</th>${r.bytes.map(v=>`<td>${v}</td>`).join('')}</tr></tbody></table><p>饱和字节和 S = ${r.sum}；L = 8 × 0.1 + ${delta} × ${r.sum} = ${fixed(r.lower,2)}。本例为看清向下取整，假定小表值恰好等于完整表值；实际最小值表还会进一步放松下界。</p><p class="decision">${r.prune?'L > τ：直接剪枝，无需完整查表。':'L ≤ τ：下界不能排除它，必须回查完整 ADC。'}${!r.prune?(r.exact>t?' 回查后 '+fixed(r.exact,2)+' > '+fixed(t,1)+'，仍被淘汰。':' 回查后 '+fixed(r.exact,2)+' ≤ '+fixed(t,1)+'，可竞争当前前 k 名。'):''}</p><p class="interaction-note">当前步长对应 qmax = m + 127Δ = ${fixed(c.minimum+127*delta,2)}，仍大于可调阈值。仅演示安全的数值下界，不模拟 CPU 吞吐量或原始向量距离。</p></div>`;};
      input.oninput=update;select.onchange=update;reset=()=>{input.value='3';select.value='0.2';update();};
    } else if(c.type==='rabitq-bound'){
      controls.innerHTML='<label>误差系数 ε₀ <input type="range" min="0.5" max="4" step="0.1" value="1.9" aria-label="RaBitQ 误差系数"></label><label>当前精确平方距离门槛 τ <input type="range" min="4.5" max="7.5" step="0.1" value="5.8" aria-label="RaBitQ 距离阈值"></label><label>最终内积的额外误差预算 <select aria-label="RaBitQ 额外误差预算"><option value="0">0（只看符号码误差）</option><option value="0.02">0.02（加上查询量化预算）</option></select></label>';
      const [epsilon,t]=controls.querySelectorAll('input'),budget=controls.querySelector('select');
      const update=()=>{const e=+epsilon.value,b=+budget.value,tau=+t.value,r=rabitqBound(c.parameters,e,b,tau);body.innerHTML=`<div aria-live="polite"><div class="number-strip"><span>ε₀ / τ<b>${fixed(e,1)} / ${fixed(tau,1)}</b></span><span>点估计 d̂²<b>${fixed(r.estimate,2)}</b></span><span>概率下界<b>${fixed(r.lower,3)}</b></span></div><p>符号码内积误差界 E = (0.6/0.8) × ${fixed(e,1)} / √255 = ${fixed(r.E,5)}。加上最终内积预算 ${fixed(b,2)}，距离半径 R = 2 × 2 × 3 × (E + ${fixed(b,2)}) = ${fixed(r.radius,3)}。</p><div class="bound-line"><span>下界 ${fixed(r.lower,3)}</span><b>← 7 ± ${fixed(r.radius,3)} →</b><span>上界 ${fixed(r.estimate+r.radius,3)}</span></div><p class="decision">${r.prune?'下界 > τ：在界成立的事件上，可排除该候选。':'下界 ≤ τ：不能安全排除，读取原向量精算。'} 点估计始终为 7；改变误差预算可以改变是否回查。</p><p class="interaction-note">D=256、a=0.8、rₒ=2、r_q=3、分子=0.4，都是构造输入。较大的 ε₀ 放宽区间，并降低理论尾界；此处没有已知常数可换算成“99% 置信度”。额外预算是教学输入，不等于论文查询量化误差的实测值。</p></div>`;};
      epsilon.oninput=update;t.oninput=update;budget.onchange=update;reset=()=>{epsilon.value='1.9';t.value='5.8';budget.value='0';update();};
    } else return;
    panel.querySelector('.interaction-reset').onclick=reset;reset();
    host.innerHTML='';const staticText=document.createElement('div');staticText.className='interactive-fallback';staticText.innerHTML=fallback;host.append(panel,staticText);host.classList.add('interactive','enhanced');
  } catch(e){host.innerHTML=fallback;console.warn('Interactive fallback retained',e);}
}
const api={render,pqBound,rabitqBound};global.PaperInteractions=api;
if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
