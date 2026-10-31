export type StudySummary = {
  n: number; already_at_target: number; expiry_dates: number;
  closer_rate: number | null; mirror_rate: number | null; moved_toward_rate: number | null;
  range_reached_rate: number | null; median_gap_reduction_pct_points: number | null;
  mean_start_gap_pct: number | null; mean_end_gap_pct: number | null; difference_vs_mirror: number | null;
};
export type StudyGroup = {
  horizon: number; proximity: "near" | "all"; coverage_mode: "strict" | "published"; summary: StudySummary;
  confidence: { method: string; repeats: number; seed: number; rate_low: number; rate_high: number; difference_low: number; difference_high: number } | null;
  by_asset: (StudySummary & { symbol: string; label: string })[];
  by_month: (StudySummary & { month: string })[];
  data_coverage: { eligible: number; excluded: number; coverage_pct: number | null };
};
export type StudyObservation = {
  symbol: string; label: string; expiry: string; snapshot_date: string; entry_date: string; horizon: number;
  target: number; entry_open: number; expiry_close: number; start_gap_pct: number; end_gap_pct: number;
  closer: boolean | null; moved_toward: boolean | null; range_reached_target: boolean; near: boolean;
  mirror_closer: boolean | null; gap_reduction_pct_points: number;
  strict_eligible: boolean; unpaired_strikes: number; unpaired_oi_pct: number;
};
export type MaxPainResearch = {
  version: string; generated_at: string; start_date: string; end_date: string;
  methodology: string[]; groups: StudyGroup[]; observations: StudyObservation[];
  exclusion_reasons: Record<string, number>;
  coverage: { symbol: string; label: string; expiries_identified: number; price_sessions: number }[];
  file_coverage: { expected_sessions: number; available_files: number; first_file: string | null; last_file: string | null };
  universe: { symbol: string; label: string; instrument_key: string }[];
  errors: { day?: string; symbol?: string; stage: string; error: string }[];
};
