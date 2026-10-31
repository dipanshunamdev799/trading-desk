// Isolated browser fixture: actual components and local dependencies, no API/DB.
const fs = require('node:fs');
const path = require('node:path');
const front = path.resolve(__dirname, '../../frontend');
const ts = require(path.join(front, 'node_modules/typescript'));
for (const [from, to] of [
  ['node_modules/react/umd/react.production.min.js', 'react.js'],
  ['node_modules/react-dom/umd/react-dom.production.min.js', 'react-dom.js'],
  ['node_modules/echarts/dist/echarts.min.js', 'echarts.js'],
  ['app/globals.css', 'style.css'],
]) fs.copyFileSync(path.join(front, from), path.join(__dirname, to));
const files = ['optionGreeksCharts.ts', 'ExpandableChartPanel.tsx', 'EChartPanel.tsx', 'OptionGreeksPanel.tsx'];
let bundle = `const modules={react:React,echarts:echarts,'react/jsx-runtime':{jsx:(t,p,k)=>React.createElement(t,{...p,key:k}),jsxs:(t,p,k)=>React.createElement(t,{...p,key:k}),Fragment:React.Fragment}}; const factories={}; function require(name){if(!modules[name]){modules[name]={};factories[name](modules[name],require);}return modules[name];}\n`;
for (const file of files) {
  const compiled = ts.transpileModule(fs.readFileSync(path.join(front, 'components', file), 'utf8'), {compilerOptions: {module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,jsx:ts.JsxEmit.ReactJSX}}).outputText;
  bundle += `factories['@/components/${file.split('.')[0]}']=function(exports,require){${compiled}\n};\n`;
}
bundle += `const sample={expiry:'2026-10-27',as_of:'2026-10-23',instrument_key:'NSE_INDEX|Nifty 50',source:'UI TEST FIXTURE',observed_at:'2026-10-23T15:25:00+05:30',reported_at:null,status:'historical',spot:22620,data_available:true,available:42,required:42,complete_legs:41,complete:false,hint:'TEST FIXTURE: one Gamma is deliberately missing.',basis:'TEST FIXTURE — synthetic per-option values; not market data.',rows:Array.from({length:21},(_,i)=>({strike:22100+i*50,call:{delta:.9-i*.04,gamma:i===0?null:.000123,theta:-12.5,vega:8.3,iv:15.2},put:{delta:-.1-i*.04,gamma:i===20?0:.00012,theta:-11.2,vega:8.3,iv:16.1}}))};
function Preview(){const [strike,setStrike]=React.useState(null);return React.createElement(require('@/components/OptionGreeksPanel').default,{data:sample,expiry:sample.expiry,asOf:sample.as_of,loading:false,selectedStrike:strike,onSelectStrike:setStrike});}
ReactDOM.createRoot(document.getElementById('fixture')).render(React.createElement(Preview));`;
fs.writeFileSync(path.join(__dirname, 'fixture.js'), bundle);
fs.writeFileSync(path.join(__dirname, 'index.html'), `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Option Greeks — isolated UI test fixture</title><link rel="stylesheet" href="style.css"><body><main style="max-width:1450px;margin:auto;padding:20px"><div class="error-box" style="margin-bottom:16px">UI TEST FIXTURE — SYNTHETIC VALUES, NOT MARKET DATA. This page does not use or modify the application database.</div><div id="fixture"></div></main><script src="react.js"></script><script src="react-dom.js"></script><script src="echarts.js"></script><script src="fixture.js"></script></body></html>`);
console.log('Built isolated interactive Greeks preview.');
