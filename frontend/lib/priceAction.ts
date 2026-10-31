import type { CandleSeries } from "./api";

export type StudyEvent = {
  id: string; concept: number; group: string; label: string; ts: string; known_at: string;
  side: number; price: number; level: number | null; detail: string;
};
export type StudyLine = { concept: number; group: string; label: string; side: number; points: { ts: string; value: number }[] };
export type StudyZone = {
  concept: number; group: string; label: string; start: string; end: string;
  low: number; high: number; side: number; tested: boolean; active: boolean;
};
export type PriceActionStudy = {
  version: string; session: string | null; sessions: string[]; groups: { id: string; label: string }[];
  catalog: { id: number; group: string; label: string; rule: string }[];
  events: StudyEvent[]; lines: StudyLine[]; zones: StudyZone[]; trend: string;
  completed_bars: number; forming_bars: number; confirmed_through: string | null;
  notes: string[]; orb_minutes: number; round_step: number; previous_session: string | null;
  atr?: number | null; level_tolerance?: number; missing_bars?: number;
};
export type PriceActionResponse = CandleSeries & { study: PriceActionStudy };
export type StudyOverlay = { events: StudyEvent[]; lines: StudyLine[]; zones: StudyZone[]; focus?: string | null };
export const CORE_CONCEPTS = new Set([1, 2, 4, 5, 6, 7, 8, 9, 11, 13, 14, 15, 20, 21, 22, 32, 33, 39, 42]);
export const istDay = (ts: string) => new Date(Date.parse(ts) + 19800000).toISOString().slice(0, 10);
export const studyTime = (ts: string | null) => ts ? new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
}).format(new Date(ts)) : "—";
export const studyColor = (side: number) => side > 0 ? "#2DD4A8" : side < 0 ? "#F07178" : "#E7BD72";
export function compactStudyLabel(event: StudyEvent) {
  if (["HH", "HL", "LH", "LL", "BOS", "CHoCH"].includes(event.label)) return event.label;
  const names: Record<number, string> = { 1: "HH/HL", 2: "LH/LL", 3: "RNG", 4: "SUP", 5: "RES", 6: "FLIP", 10: "EQL", 11: "SWP", 13: "RET↑", 14: "RET↓", 15: "FAIL", 16: "DBL", 17: "H&S", 18: "iH&S", 19: "TL", 21: "ENG↑", 22: "ENG↓", 23: "HMR", 24: "STAR", 25: "DOJI", 26: "IN", 27: "OUT", 28: "MAR", 29: "MS", 30: "ES", 31: "PIN", 32: "PB↑", 33: "PB↓", 34: "FLAG↑", 35: "FLAG↓", 36: "TRI↑", 37: "TRI↓", 38: "TRI", 39: "ORB", 40: "MOM", 41: "VOL", 43: "OB?", 44: "FVG", 45: "S/D?", 46: "DISP", 47: "TEST" };
  return names[event.concept] || event.label;
}

export type ConceptUsage = Record<number, number>;
export const CONCEPT_USAGE_KEY = "nifty.priceAction.conceptUsage.v1";
export function parseConceptUsage(raw: string | null): ConceptUsage {
  try {
    const parsed = JSON.parse(raw || "{}");
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return {};
    const usage: ConceptUsage = {};
    for (const [key, count] of Object.entries(parsed)) {
      const id = Number(key);
      if (Number.isInteger(id) && id >= 1 && id <= 47 && typeof count === "number" && Number.isSafeInteger(count) && count > 0) usage[id] = count;
    }
    return usage;
  } catch { return {}; }
}
export function frequentConcepts(catalog: PriceActionStudy["catalog"], usage: ConceptUsage) {
  return catalog.filter(row => usage[row.id] > 0).sort((a, b) => usage[b.id] - usage[a.id] || a.id - b.id).slice(0, 6);
}

export function selectStudy(study: PriceActionStudy | null, groups: string[], preset: string, concept: number | null, selectedConcepts?: number[]): StudyOverlay {
  const allowed = (row: { concept: number; group: string }) => selectedConcepts != null
    ? preset !== "none" && (preset === "all" || selectedConcepts.includes(row.concept))
    : concept != null ? row.concept === concept
    : groups.includes(row.group) && (preset !== "core" || CORE_CONCEPTS.has(row.concept));
  return { events: (study?.events || []).filter(allowed), lines: (study?.lines || []).filter(allowed), zones: (study?.zones || []).filter(allowed) };
}
