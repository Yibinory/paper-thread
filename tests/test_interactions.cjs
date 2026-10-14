const assert=require('node:assert/strict');
const {pqBound,rabitqBound}=require('../web/interactions.js');
const values=[.33,.51,.76,.28,.44,.61,.55,.37];
const coarse=pqBound(values,.1,.2,3);
assert.deepEqual(coarse.bytes,[1,2,3,0,1,2,2,1]);
assert.ok(Math.abs(coarse.lower-3.2)<1e-12);assert.equal(coarse.prune,true);
assert.equal(pqBound(values,.1,.2,3.5).prune,false);
assert.equal(pqBound(values,.1,.05,3.5).prune,true);
assert.equal(pqBound(values,.1,.2,3.2).prune,false); // Preserve ties for exact refinement.
for(const delta of [.05,.2])for(let i=0;i<2000;i++){
 const v=Array.from({length:8},(_,j)=>.1+((i*37+j*53)%911)/13);
 const r=pqBound(v,.1,delta,4.5);
 assert.ok(r.lower<=r.exact+1e-10);assert.ok(r.sum<=127);
 if(r.prune)assert.ok(r.exact>4.5);
}
const p={dimension:256,a:.8,ro:2,rq:3,numerator:.4};
const a=rabitqBound(p,1.9,0,5.8),b=rabitqBound(p,1.9,.02,5.8);
assert.ok(Math.abs(a.estimate-7)<1e-12);assert.equal(a.estimate,b.estimate);
assert.ok(a.lower>5.92&&a.lower<5.94);assert.equal(a.prune,true);assert.equal(b.prune,false);
for(let epsilon=.5;epsilon<4;epsilon+=.1){
 const current=rabitqBound(p,epsilon,0,5.8),next=rabitqBound(p,epsilon+.1,0,5.8);
 assert.ok(next.lower<current.lower);assert.ok(next.radius>current.radius);
}
console.log('Interaction arithmetic: bound invariants, saturation, ties and decision changes passed.');
const {logitPoint,regularizedLogit}=require('../web/interactions.js');
const toy={fixed_logit:.5,initial_feature:1,feature_weight:1.5,max_shift:2};
assert.ok(Math.abs(logitPoint(toy,.2,0).loss-Math.log1p(Math.exp(-2)))<1e-12);
assert.ok(Math.abs(logitPoint(toy,.2,2).objective-(Math.log1p(Math.exp(1))-.8))<1e-12);
assert.equal(regularizedLogit(toy,0).best.omega,2);
assert.ok(regularizedLogit(toy,.8).best.omega<.2);
let previous=Infinity;
for(let l=0;l<=.8+1e-10;l+=.01){
 const r=regularizedLogit(toy,l);
 assert.ok(r.best.omega<=previous+1e-12);previous=r.best.omega;
 for(const q of r.points){
  assert.ok(Number.isFinite(q.objective)&&q.probability>0&&q.probability<1);
  assert.ok(q.objective<=q.loss+1e-12);
  const h=1e-5,difference=(logitPoint(toy,l,q.omega+h).objective-logitPoint(toy,l,q.omega-h).objective)/(2*h);
  assert.ok(Math.abs(difference-q.gradient)<1e-8);
 }
 // Compare against a denser independent scan, allowing the reported grid precision.
 let dense=-Infinity;for(let i=0;i<=4000;i++)dense=Math.max(dense,logitPoint(toy,l,2*i/4000).objective);
 assert.ok(dense-r.best.objective<1e-5);
}
for(const fixed of [-20,20])for(const weight of [.01,20]){
 const r=regularizedLogit({fixed_logit:fixed,initial_feature:-20,feature_weight:weight,max_shift:20},10);
 assert.ok(r.points.every(q=>Number.isFinite(q.loss)&&Number.isFinite(q.objective)));
}
console.log('Logit example: analytical gradient, grid maximum, penalty monotonicity and numerical stability passed.');
