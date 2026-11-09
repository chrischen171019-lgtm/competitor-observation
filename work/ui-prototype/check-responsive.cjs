const fs=require('fs');const s=fs.readFileSync('outputs/competitor-ui-prototype.html','utf8');
for(const x of ['Global responsive system:','@media (max-width:760px)','@media (max-width:420px)','overflow-x:auto','width=device-width'])if(!s.includes(x))throw Error('missing '+x);
if(!s.includes('body>aside.app-sidebar{width:100%'))throw Error('mobile nav missing');
if(!s.includes('.digest-layout{display:block'))throw Error('mobile digest missing');
const viewport=(s.match(/name="viewport"/g)||[]).length;if(!viewport)throw Error('viewport missing');
console.log('PASS: responsive CSS, viewport metadata, mobile navigation, digest collapse, overflow containment.');