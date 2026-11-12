const paths: Record<string, string> = {
  home: "m3 10 9-7 9 7M5 9v12h5v-7h4v7h5V9",
  book: "M12 5C8 2 3 4 3 4v15s5-2 9 1c4-3 9-1 9-1V4s-5-2-9 1Zm0 0v15",
  chart: "M4 4v16h16M7 14l4-5 4 3 5-7",
  layers: "m12 2 10 5-10 5L2 7l10-5Zm-9 10 9 5 9-5M3 17l9 5 9-5",
  building: "M5 21V5l10-2v18M15 10h5v11M3 21h19M8 8h4M8 12h4M8 16h4M17 14h1M17 17h1",
  history: "M3 10a9 9 0 1 1 1 7M3 4v6h6M12 7v5l3 2",
  wallet: "M20 8V5a2 2 0 0 0-2-2H5a3 3 0 0 0 0 6h16v11H5a3 3 0 0 1-3-3V6m19 7h-5v4h5",
  sliders: "M4 3v7m0 4v7M12 3v12m0 4v2M20 3v2m0 4v12M1 10h6M9 15h6M17 5h6",
  bot: "M12 3v3m-5 0h10a3 3 0 0 1 3 3v9H4V9a3 3 0 0 1 3-3ZM8 11v2m8-2v2M8 18v3m8-3v3M1 10v5m22-5v5",
  spread: "M3 6h13m-4-4 4 4-4 4M21 18H8m4-4-4 4 4 4",
  database: "M20 6c0 2-4 3-8 3S4 8 4 6s4-3 8-3 8 1 8 3Zm0 0v12c0 2-4 3-8 3s-8-1-8-3V6m0 6c0 2 4 3 8 3s8-1 8-3",
  search: "m16 16 5 5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z",
  arrow: "M5 12h14m-5-5 5 5-5 5", chevron: "m9 5 7 7-7 7",
  help: "M9 9a3 3 0 1 1 5 2c-2 1-2 2-2 3m0 3h.01M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z",
  menu: "M4 6h16M4 12h16M4 18h16", close: "m6 6 12 12M6 18 18 6", check: "m5 12 4 4L19 6",
};
export default function DeskIcon({ name, size = 20 }: { name: string; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name] || paths.chart} /></svg>;
}
