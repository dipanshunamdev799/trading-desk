const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");
const echarts = require("echarts");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
function load(file, deps={}) {
  const code = ts.transpileModule(fs.readFileSync(path.join(__dirname,file),"utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  const exports={}; new Function("exports","require",code)(exports,name=>deps[name]||require(name)); return exports;
}
const charts=load("../components/maxpainStudyCharts.ts");
const summary={n:40,already_at_target:0,expiry_dates:12,closer_rate:55,mirror_rate:40,moved_toward_rate:60,range_reached_rate:70,median_gap_reduction_pct_points:.12,mean_start_gap_pct:.5,mean_end_gap_pct:.4,difference_vs_mirror:15};
const group={horizon:1,proximity:"near",summary,confidence:{difference_low:-2,difference_high:30,rate_low:40,rate_high:70},data_coverage:{eligible:50,excluded:2,coverage_pct:96},by_asset:[{...summary,symbol:"NIFTY",label:"Nifty 50"},{...summary,n:0,symbol:"TCS",label:"TCS",closer_rate:null,mirror_rate:null}],by_month:[{...summary,month:"2026-10"}]};
group.coverage_mode = "strict";
const component=load("../components/MaxPainStudy.tsx",{
  "./Bits":{Metric:({label,value})=>React.createElement("p",null,label," ",value)},
  "./EChartPanel":{default:()=>null},"./ExpandableChartPanel":{default:({children})=>React.createElement("div",null,children)},"./maxpainStudyCharts":charts,
});
test("research shows its denominator, uncertainty and control without inventing trading performance",()=>{
 const study={start_date:"2025-10-25",end_date:"2026-10-24",groups:[group],observations:[],methodology:["Freeze the earlier target"],universe:[],coverage:[],errors:[],exclusion_reasons:{},file_coverage:{available_files:255,expected_sessions:255},generated_at:"2026-10-25T10:00:00Z",version:"test"};
 const html=renderToStaticMarkup(React.createElement(component.default,{study}));
 for(const value of ["40 · 12 expiry dates","55.0%","40.0%","uncertainty interval includes no difference","Snapshot timing","Within 1%","95% expiry-date bootstrap interval","255/255","no strategy P&amp;L"]) assert.ok(html.includes(value),value);
 for(const value of ["Equity curve","Sharpe","Win rate"]) assert.ok(!html.includes(value),value);
});
test("chart preserves missing results, explicit sample sizes and percent scale",()=>{
 const option=charts.chainConvergenceOption(group);
 assert.equal(option.yAxis.max,100);assert.equal(option.series[0].data[1],null);assert.ok(option.xAxis.data[1].includes("n=0"));
 const chart=echarts.init(null,null,{renderer:"svg",ssr:true,width:1000,height:330});
 try{chart.setOption(option);assert.ok(chart.renderToSVGString().includes("Frozen Max Pain"));}finally{chart.dispose();}
});
