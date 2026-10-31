const modules={react:React,echarts:echarts,'react/jsx-runtime':{jsx:(t,p,k)=>React.createElement(t,{...p,key:k}),jsxs:(t,p,k)=>React.createElement(t,{...p,key:k}),Fragment:React.Fragment}}; const factories={}; function require(name){if(!modules[name]){modules[name]={};factories[name](modules[name],require);}return modules[name];}
factories['@/components/optionGreeksCharts']=function(exports,require){"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GREEK_LABELS = void 0;
exports.formatGreek = formatGreek;
exports.focusGreekStrike = focusGreekStrike;
exports.greekChartOption = greekChartOption;
exports.GREEK_LABELS = { delta: "Delta", gamma: "Gamma", theta: "Theta", vega: "Vega", iv: "IV (%)" };
function formatGreek(value, metric) {
    if (value == null || !Number.isFinite(value))
        return "—";
    const digits = metric === "gamma" ? 6 : metric === "iv" ? 2 : 4;
    return value.toLocaleString("en-IN", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}
function focusGreekStrike(rows, spot, selection) {
    if (rows.some(row => row.strike === selection))
        return selection;
    if (!rows.length)
        return null;
    if (spot == null || !Number.isFinite(spot))
        return rows[0].strike;
    return rows.reduce((best, row) => Math.abs(row.strike - spot) < Math.abs(best.strike - spot) ? row : best).strike;
}
function greekChartOption(data, metric, focus) {
    const label = exports.GREEK_LABELS[metric];
    const markers = [];
    if (data.spot != null)
        markers.push({ xAxis: data.spot, name: "Spot at capture", label: { formatter: `Spot ${data.spot.toLocaleString("en-IN")}`, position: "insideEndTop", color: "#8B9AAB" }, lineStyle: { color: "#8B9AAB", type: "dotted" } });
    if (focus != null)
        markers.push({ xAxis: focus, name: "Selected strike", label: { formatter: `Strike ${focus.toLocaleString("en-IN")}`, position: "insideStartTop", color: "#2DD4A8" }, lineStyle: { color: "#2DD4A8", type: "dashed" } });
    return {
        backgroundColor: "transparent", animation: false,
        legend: { top: 4, data: ["Call", "Put"], textStyle: { color: "#8B9AAB" } },
        grid: { left: metric === "gamma" ? 90 : 76, right: 28, top: 45, bottom: 56 },
        tooltip: { trigger: "axis", confine: true, backgroundColor: "#121820", borderColor: "#243041", textStyle: { color: "#E8EDF2" },
            formatter: (input) => {
                const items = (Array.isArray(input) ? input : [input]);
                return [`Strike ${Number(items[0]?.axisValue).toLocaleString("en-IN")}`, ...items.map(item => `${item.seriesName} ${label}: ${item.value?.[1] == null ? "Unavailable" : formatGreek(item.value[1], metric)}`)].join("<br/>");
            } },
        xAxis: { type: "value", min: "dataMin", max: "dataMax", scale: true, name: "Strike", nameLocation: "middle", nameGap: 33,
            nameTextStyle: { color: "#8B9AAB" }, axisLabel: { color: "#8B9AAB", hideOverlap: true }, splitLine: { show: false } },
        yAxis: { type: "value", name: label, nameTextStyle: { color: "#8B9AAB" }, axisLabel: { color: "#8B9AAB", formatter: (value) => formatGreek(value, metric) }, splitLine: { lineStyle: { color: "#1A2330" } } },
        series: [['call', '#E06C75', 'Call'], ['put', '#61AFEF', 'Put']].map(([side, color, name], index) => ({
            name, type: "line", connectNulls: false, showSymbol: data.rows.length < 25, symbolSize: 5,
            data: data.rows.map(row => [row.strike, row[side][metric]]), itemStyle: { color }, lineStyle: { width: 2 },
            ...(index === 0 ? { markLine: { silent: true, symbol: "none", data: markers } } : {}),
        })),
    };
}

};
factories['@/components/ExpandableChartPanel']=function(exports,require){"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useExpandedChart = useExpandedChart;
exports.default = ExpandableChartPanel;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const ExpandedChartContext = (0, react_1.createContext)(false);
function useExpandedChart() {
    return (0, react_1.useContext)(ExpandedChartContext);
}
function ExpandableChartPanel({ title, children }) {
    const [expanded, setExpanded] = (0, react_1.useState)(false);
    const panelRef = (0, react_1.useRef)(null);
    const buttonRef = (0, react_1.useRef)(null);
    (0, react_1.useEffect)(() => {
        if (!expanded)
            return;
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        function handleKeyDown(event) {
            if (event.key === "Escape") {
                event.preventDefault();
                event.stopPropagation();
                setExpanded(false);
            }
            else if (event.key === "Tab") {
                const controls = Array.from(panelRef.current?.querySelectorAll('button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), summary, [tabindex="0"]') ?? []).filter((element) => element.getClientRects().length > 0);
                const first = controls[0];
                const last = controls[controls.length - 1];
                if (!panelRef.current?.contains(document.activeElement)) {
                    event.preventDefault();
                    (event.shiftKey ? last : first)?.focus();
                }
                else if (event.shiftKey && document.activeElement === first) {
                    event.preventDefault();
                    last?.focus();
                }
                else if (!event.shiftKey && document.activeElement === last) {
                    event.preventDefault();
                    first?.focus();
                }
            }
        }
        document.addEventListener("keydown", handleKeyDown, true);
        return () => {
            document.removeEventListener("keydown", handleKeyDown, true);
            document.body.style.overflow = previousOverflow;
            buttonRef.current?.focus({ preventScroll: true });
        };
    }, [expanded]);
    return ((0, jsx_runtime_1.jsx)(ExpandedChartContext.Provider, { value: expanded, children: (0, jsx_runtime_1.jsxs)("div", { ref: panelRef, className: `panel expandable-chart-panel${expanded ? " is-maximized" : ""}`, role: expanded ? "dialog" : undefined, "aria-modal": expanded ? true : undefined, "aria-label": expanded ? title : undefined, children: [(0, jsx_runtime_1.jsxs)("button", { ref: buttonRef, type: "button", className: "chart-size-button", "aria-label": `${expanded ? "Restore" : "Maximize"} ${title}`, title: expanded ? "Restore chart (Esc)" : "Maximize chart", "aria-expanded": expanded, onClick: () => setExpanded((value) => !value), children: [(0, jsx_runtime_1.jsx)("svg", { width: "14", height: "14", viewBox: "0 0 20 20", fill: "none", stroke: "currentColor", strokeWidth: "1.6", "aria-hidden": "true", children: expanded ? (0, jsx_runtime_1.jsx)("path", { d: "M2 7h5V2m11 5h-5V2M2 13h5v5m11-5h-5v5" })
                                : (0, jsx_runtime_1.jsx)("path", { d: "M7 2H2v5m11-5h5v5M2 13v5h5m11-5v5h-5" }) }), (0, jsx_runtime_1.jsx)("span", { children: expanded ? "Restore" : "Maximize" })] }), children] }) }));
}

};
factories['@/components/EChartPanel']=function(exports,require){"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = EChartPanel;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const echarts = require("echarts");
const ExpandableChartPanel_1 = require("@/components/ExpandableChartPanel");
function EChartPanel({ option, height = 320, onClick, }) {
    const ref = (0, react_1.useRef)(null);
    const expanded = (0, ExpandableChartPanel_1.useExpandedChart)();
    const chartRef = (0, react_1.useRef)(null);
    const legendRef = (0, react_1.useRef)({});
    const clickRef = (0, react_1.useRef)(onClick);
    clickRef.current = onClick;
    (0, react_1.useEffect)(() => {
        const el = ref.current;
        if (!el)
            return;
        let chart = chartRef.current;
        if (!chart) {
            chart = echarts.init(el, undefined, { renderer: "canvas" });
            chartRef.current = chart;
            chart.on("click", (params) => {
                const p = params;
                clickRef.current?.({ dataIndex: p.dataIndex, name: p.name, value: p.value });
            });
            chart.on("legendselectchanged", (params) => {
                legendRef.current = params.selected;
            });
        }
        const legend = option.legend == null ? undefined : Array.isArray(option.legend)
            ? option.legend.map((entry) => ({ ...entry, selected: { ...legendRef.current, ...entry.selected } }))
            : { ...option.legend, selected: { ...legendRef.current, ...option.legend.selected } };
        chart.setOption({ ...option, legend }, true);
        chart.resize({ width: el.clientWidth, height: el.clientHeight });
        const ro = new ResizeObserver(() => {
            if (ref.current && chartRef.current) {
                chartRef.current.resize({ width: ref.current.clientWidth, height: ref.current.clientHeight });
            }
        });
        ro.observe(el);
        return () => ro.disconnect();
    }, [option, height]);
    (0, react_1.useEffect)(() => {
        return () => {
            chartRef.current?.dispose();
            chartRef.current = null;
        };
    }, []);
    return (0, jsx_runtime_1.jsx)("div", { ref: ref, className: "echart-container", style: { width: "100%", height: expanded ? "100%" : height } });
}

};
factories['@/components/OptionGreeksPanel']=function(exports,require){"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = OptionGreeksPanel;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const EChartPanel_1 = require("@/components/EChartPanel");
const ExpandableChartPanel_1 = require("@/components/ExpandableChartPanel");
const optionGreeksCharts_1 = require("@/components/optionGreeksCharts");
function timestamp(value) {
    if (!value || !Number.isFinite(Date.parse(value)))
        return "Unavailable";
    return new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", dateStyle: "medium", timeStyle: "medium" }).format(new Date(value));
}
function OptionGreeksPanel({ data, asOf, expiry, loading, selectedStrike, onSelectStrike }) {
    const [metric, setMetric] = (0, react_1.useState)("delta");
    const [range, setRange] = (0, react_1.useState)("near");
    const current = data?.as_of === asOf && data.expiry === expiry ? data : undefined;
    const rows = current?.rows || [];
    const focus = (0, optionGreeksCharts_1.focusGreekStrike)(rows, current?.spot ?? null, selectedStrike);
    const atm = (0, optionGreeksCharts_1.focusGreekStrike)(rows, current?.spot ?? null, null);
    const center = rows.findIndex(row => row.strike === focus);
    const visible = range === "all" ? rows : rows.slice(Math.max(0, center - 5), center + 6);
    const option = (0, react_1.useMemo)(() => current ? (0, optionGreeksCharts_1.greekChartOption)(current, metric, focus) : null, [current, metric, focus]);
    const ready = current?.data_available;
    const header = current?.status === "historical" ? "Saved session snapshot" : current?.status === "retained" ? "Retained snapshot" : "Captured snapshot";
    return (0, jsx_runtime_1.jsxs)("section", { className: "stack maxpain-greeks", "aria-label": "Option Greeks", children: [(0, jsx_runtime_1.jsxs)("div", { className: "panel", children: [(0, jsx_runtime_1.jsxs)("div", { className: "panel-header", children: [(0, jsx_runtime_1.jsxs)("div", { children: [(0, jsx_runtime_1.jsx)("h2", { children: "Option Greeks" }), (0, jsx_runtime_1.jsx)("p", { className: "maxpain-caption", children: "Delta \u00B7 Gamma \u00B7 Theta \u00B7 Vega \u00B7 IV \u00B7 calls & puts" }), (0, jsx_runtime_1.jsxs)("p", { className: "maxpain-caption", children: ["Expiry ", expiry || "—", " \u00B7 as of ", asOf, " IST"] })] }), ready && (0, jsx_runtime_1.jsxs)("span", { className: `badge ${current.status === "retained" ? "warn" : "db"}`, children: [current.available, "/", current.required, " legs with data \u00B7 ", header] })] }), ready ? (0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [(0, jsx_runtime_1.jsxs)("div", { className: "panel-body greek-controls", children: [(0, jsx_runtime_1.jsxs)("div", { className: "greek-source", children: [(0, jsx_runtime_1.jsx)("a", { href: "https://upstox.com/developer/api-documentation/get-pc-option-chain/", target: "_blank", rel: "noreferrer", children: "Upstox option chain \u2197" }), (0, jsx_runtime_1.jsxs)("span", { children: ["Captured ", timestamp(current.observed_at), " IST"] }), (0, jsx_runtime_1.jsx)("span", { children: "Source market timestamp not supplied" })] }), (0, jsx_runtime_1.jsxs)("div", { className: "row", children: [(0, jsx_runtime_1.jsxs)("div", { className: "field", children: [(0, jsx_runtime_1.jsx)("label", { htmlFor: "greek-focus-strike", children: "Focus strike" }), (0, jsx_runtime_1.jsx)("select", { id: "greek-focus-strike", value: focus ?? "", onChange: event => onSelectStrike(Number(event.target.value)), children: rows.map(row => (0, jsx_runtime_1.jsxs)("option", { value: row.strike, children: [row.strike.toLocaleString("en-IN"), row.strike === atm && current.spot != null ? " · nearest spot" : ""] }, row.strike)) })] }), (0, jsx_runtime_1.jsxs)("div", { className: "field", children: [(0, jsx_runtime_1.jsx)("label", { htmlFor: "greek-table-range", children: "Strike range" }), (0, jsx_runtime_1.jsxs)("select", { id: "greek-table-range", value: range, onChange: event => setRange(event.target.value), children: [(0, jsx_runtime_1.jsx)("option", { value: "near", children: "Near focus (\u00B15 strikes)" }), (0, jsx_runtime_1.jsx)("option", { value: "all", children: "All strikes" })] })] })] }), current.hint && (0, jsx_runtime_1.jsx)("p", { className: "greek-coverage", role: "status", children: current.hint }), current.status === "historical" && (0, jsx_runtime_1.jsx)("p", { className: "greek-coverage", children: "This is the latest snapshot saved that session, with its original capture time. It is not necessarily the closing Greeks." }), current.status === "retained" && (0, jsx_runtime_1.jsx)("p", { className: "greek-coverage", children: "Showing a previously captured snapshot. Check its capture time before comparing with newer OI or spot readings." })] }), (0, jsx_runtime_1.jsx)("div", { className: "table-wrap greek-table-wrap", children: (0, jsx_runtime_1.jsxs)("table", { className: "data greek-table", children: [(0, jsx_runtime_1.jsxs)("caption", { className: "sr-only", children: ["Per-option call and put Greeks by strike for ", expiry, " on ", asOf] }), (0, jsx_runtime_1.jsxs)("thead", { children: [(0, jsx_runtime_1.jsxs)("tr", { children: [(0, jsx_runtime_1.jsx)("th", { colSpan: 5, className: "greek-call", children: "Call" }), (0, jsx_runtime_1.jsx)("th", { rowSpan: 2, className: "greek-strike", children: "Strike" }), (0, jsx_runtime_1.jsx)("th", { colSpan: 5, className: "greek-put", children: "Put" })] }), (0, jsx_runtime_1.jsxs)("tr", { children: [["iv", "vega", "theta", "gamma", "delta"].map(key => (0, jsx_runtime_1.jsx)("th", { className: "num greek-call", scope: "col", children: optionGreeksCharts_1.GREEK_LABELS[key] }, `call-${key}`)), ["delta", "gamma", "theta", "vega", "iv"].map(key => (0, jsx_runtime_1.jsx)("th", { className: "num greek-put", scope: "col", children: optionGreeksCharts_1.GREEK_LABELS[key] }, `put-${key}`))] })] }), (0, jsx_runtime_1.jsx)("tbody", { children: visible.map(row => (0, jsx_runtime_1.jsxs)("tr", { className: row.strike === focus ? "is-selected" : undefined, children: [["iv", "vega", "theta", "gamma", "delta"].map(key => (0, jsx_runtime_1.jsx)("td", { className: "num mono", children: (0, optionGreeksCharts_1.formatGreek)(row.call[key], key) }, `call-${key}`)), (0, jsx_runtime_1.jsx)("th", { scope: "row", className: "greek-strike", children: (0, jsx_runtime_1.jsxs)("button", { type: "button", "aria-pressed": row.strike === focus, onClick: () => onSelectStrike(row.strike), children: [row.strike.toLocaleString("en-IN"), row.strike === atm && current.spot != null && (0, jsx_runtime_1.jsx)("small", { children: "nearest spot" })] }) }), ["delta", "gamma", "theta", "vega", "iv"].map(key => (0, jsx_runtime_1.jsx)("td", { className: "num mono", children: (0, optionGreeksCharts_1.formatGreek)(row.put[key], key) }, `put-${key}`))] }, row.strike)) })] }) }), (0, jsx_runtime_1.jsxs)("div", { className: "panel-body greek-help", children: [(0, jsx_runtime_1.jsxs)("p", { children: [current.basis, " Missing fields show \u2014; a supplied zero remains zero."] }), (0, jsx_runtime_1.jsxs)("details", { children: [(0, jsx_runtime_1.jsx)("summary", { children: "What do these fields mean?" }), (0, jsx_runtime_1.jsxs)("p", { children: [(0, jsx_runtime_1.jsx)("strong", { children: "Delta" }), " describes premium sensitivity to the underlying price. ", (0, jsx_runtime_1.jsx)("strong", { children: "Gamma" }), " describes how Delta changes. ", (0, jsx_runtime_1.jsx)("strong", { children: "Theta" }), " describes time sensitivity. ", (0, jsx_runtime_1.jsx)("strong", { children: "Vega" }), " describes volatility sensitivity. ", (0, jsx_runtime_1.jsx)("strong", { children: "IV" }), " is implied volatility, rather than a Greek."] }), (0, jsx_runtime_1.jsx)("p", { children: "These are provider model values for individual options. Theta/Vega follow the provider\u2019s scaling conventions. They are not an OI-weighted exposure or a directional forecast. Rho is not supplied by this option-chain endpoint." })] })] })] }) : (0, jsx_runtime_1.jsx)("div", { className: "chart-empty greek-empty", role: "status", children: loading ? "Loading option Greeks…" : current?.hint || "Option Greeks are unavailable for this selection." })] }), ready && option && (0, jsx_runtime_1.jsxs)(ExpandableChartPanel_1.default, { title: "Option Greeks by strike", children: [(0, jsx_runtime_1.jsxs)("div", { className: "panel-header", children: [(0, jsx_runtime_1.jsxs)("div", { children: [(0, jsx_runtime_1.jsx)("h2", { children: "Option Greeks by strike" }), (0, jsx_runtime_1.jsx)("p", { className: "maxpain-caption", children: "Per-option values \u00B7 lines use the same saved snapshot as the table" })] }), (0, jsx_runtime_1.jsxs)("div", { className: "field", children: [(0, jsx_runtime_1.jsx)("label", { htmlFor: "greek-chart-metric", children: "Chart metric" }), (0, jsx_runtime_1.jsx)("select", { id: "greek-chart-metric", value: metric, onChange: event => setMetric(event.target.value), children: Object.entries(optionGreeksCharts_1.GREEK_LABELS).map(([key, label]) => (0, jsx_runtime_1.jsx)("option", { value: key, children: label }, key)) })] })] }), (0, jsx_runtime_1.jsx)("div", { className: "panel-body tight", children: (0, jsx_runtime_1.jsx)(EChartPanel_1.default, { option: option, height: 290, onClick: event => { const row = rows[event.dataIndex]; if (row)
                                onSelectStrike(row.strike); } }) })] })] });
}

};
const sample={expiry:'2026-10-27',as_of:'2026-10-23',instrument_key:'NSE_INDEX|Nifty 50',source:'UI TEST FIXTURE',observed_at:'2026-10-23T15:25:00+05:30',reported_at:null,status:'historical',spot:22620,data_available:true,available:42,required:42,complete_legs:41,complete:false,hint:'TEST FIXTURE: one Gamma is deliberately missing.',basis:'TEST FIXTURE — synthetic per-option values; not market data.',rows:Array.from({length:21},(_,i)=>({strike:22100+i*50,call:{delta:.9-i*.04,gamma:i===0?null:.000123,theta:-12.5,vega:8.3,iv:15.2},put:{delta:-.1-i*.04,gamma:i===20?0:.00012,theta:-11.2,vega:8.3,iv:16.1}}))};
function Preview(){const [strike,setStrike]=React.useState(null);return React.createElement(require('@/components/OptionGreeksPanel').default,{data:sample,expiry:sample.expiry,asOf:sample.as_of,loading:false,selectedStrike:strike,onSelectStrike:setStrike});}
ReactDOM.createRoot(document.getElementById('fixture')).render(React.createElement(Preview));