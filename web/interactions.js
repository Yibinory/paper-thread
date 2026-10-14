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
// A stated teaching model: y=1, b'=b-omega, z=fixed_logit+w*b'.
// Enumerate a finite grid; this is not a simulation of neural-network training.
function logitPoint(p,lambda,omega){
  const feature=p.initial_feature-omega,z=p.fixed_logit+p.feature_weight*feature;
  const probability=z>=0?1/(1+Math.exp(-z)):Math.exp(z)/(1+Math.exp(z));
  const loss=Math.max(-z,0)+Math.log1p(Math.exp(-Math.abs(z)));
  return {omega,feature,z,probability,loss,penalty:lambda*omega*omega,
    objective:loss-lambda*omega*omega,gradient:p.feature_weight*(1-probability)-2*lambda*omega};
}
function regularizedLogit(p,lambda){
  const points=Array.from({length:401},(_,i)=>logitPoint(p,lambda,p.max_shift*i/400));
  const best=points.reduce((a,b)=>b.objective>a.objective?b:a);
  return {points,best,original:points[0],gridStep:p.max_shift/400};
}
function logitFigure(c,lambda){
  const p=c.parameters,r=regularizedLogit(p,lambda),high=regularizedLogit(p,c.lambda_range.max);
  const lo=Math.min(0,...high.points.map(d=>d.objective))-.12,hi=Math.max(...r.points.map(d=>d.loss))+.2;
  const X=v=>58+v/p.max_shift*440,Y=v=>218-(v-lo)/(hi-lo)*180;
  const path=key=>r.points.map((d,i)=>`${i?'L':'M'}${X(d.omega).toFixed(2)},${Y(d[key]).toFixed(2)}`).join(' ');
  const xs=[0,p.max_shift/2,p.max_shift],ys=[lo,(lo+hi)/2,hi];
  const ticks=xs.map(x=>`<text x="${X(x)}" y="242" text-anchor="middle">${fixed(x,1)}</text>`).join('')+ys.map(y=>`<path class="plot-grid" d="M58 ${Y(y)}H498"/><text x="48" y="${Y(y)+5}" text-anchor="end">${fixed(y,1)}</text>`).join('');
  const b=r.best;
  return `<div class="mechanism-plot" tabindex="0" role="region" aria-label="目标曲线，可横向滚动"><svg viewBox="0 0 550 275" role="img" aria-label="惩罚权重 ${fixed(lambda,2)} 时，网格最优强度 ${fixed(b.omega,3)}，正确类概率 ${fixed(b.probability,3)}。虚线是分类损失，实线是扣除距离惩罚的目标。"><text x="58" y="22">损失 / 目标值</text>${ticks}<path class="plot-axis" d="M58 38V218H498"/><path class="plot-zero" d="M58 ${Y(0)}H498"/><path class="plot-loss" d="${path('loss')}"/><path class="plot-objective" d="${path('objective')}"/><path class="plot-guide" d="M${X(b.omega)} 38V218"/><circle class="plot-selected" cx="${X(b.omega)}" cy="${Y(b.objective)}" r="5"/><text x="498" y="266" text-anchor="end">变化强度 ω</text></svg></div><div class="plot-legend"><span class="role-objective">虚线：分类损失 CE</span><span class="role-transform">实线：J = CE − λω²</span><span>圆点：401 个网格点中最大值</span></div><div class="feature-track"><div>${esc(c.feature_label)}：<span class="role-input">原值 ${fixed(p.initial_feature,1)}</span> → <span class="role-transform">变换后 ${fixed(b.feature,3)}</span></div><div class="feature-axis"><span class="feature-origin" style="left:100%" aria-hidden="true"></span><span class="feature-chosen" style="left:${100*(1-b.omega/p.max_shift)}%" aria-hidden="true"></span></div><div class="feature-ends"><span>${fixed(p.initial_feature-p.max_shift,1)}</span><span>${fixed(p.initial_feature,1)}</span></div></div><p class="mechanism-readout" aria-live="polite" aria-atomic="true">ω ≈ ${fixed(b.omega,3)}，分类得分 z = ${fixed(b.z,3)}，<span class="role-prediction">正确类概率 ${fixed(b.probability,3)}</span>。CE ${fixed(b.loss,3)} − 惩罚 ${fixed(b.penalty,3)} = J ${fixed(b.objective,3)}。${b.probability<.5?'此时示例分类器预测错误。':'此时示例分类器仍预测正确。'}</p>`;
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
    if(c.type==='regularized-logit'){
      panel.classList.add('mechanism-ui');
      const r=c.lambda_range;
      controls.innerHTML=`<label class="mechanism-control">距离惩罚 λ <input type="range" min="${r.min}" max="${r.max}" step="${r.step}" value="${r.initial}" aria-label="距离惩罚权重 λ"><output>${fixed(r.initial,2)}</output></label>`;
      const input=controls.querySelector('input'),output=controls.querySelector('output');
      const update=()=>{output.textContent=fixed(+input.value,2);body.innerHTML=logitFigure(c,+input.value);};
      input.oninput=update;reset=()=>{input.value=String(r.initial);update();};
      // Keep the whole figure above its control, with stable input focus on redraw.
      body.after(controls);
    } else if(c.type==='trace'){
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
const api={render,pqBound,rabitqBound,logitPoint,regularizedLogit};global.PaperInteractions=api;
if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
