// Display formatting helpers. All numbers rendered here come from the API
// response — the frontend never computes risk or distance itself.

export function fmtMiles(mi: number): string {
  return `${Math.round(mi).toLocaleString("en-US")} mi`;
}

export function fmtDuration(min: number): string {
  const h = Math.floor(min / 60);
  const m = Math.round(min % 60);
  return `${h} h ${m.toString().padStart(2, "0")} m`;
}

export function fmtEta(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function fmtClock(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

export function fmtLoad(lb: number): string {
  return lb.toLocaleString("en-US");
}

/**
 * Largest-remainder rounding: percentages always sum to exactly 100.
 * Prevents the classic "risk bars sum to 98%" bug (guidebook §8).
 */
export function percentShares(values: number[]): number[] {
  const total = values.reduce((a, b) => a + b, 0);
  if (total <= 0) return values.map(() => 0);
  const exact = values.map((v) => (v / total) * 100);
  const floors = exact.map(Math.floor);
  const remainders = exact
    .map((v, i) => ({ i, r: v - floors[i] }))
    .sort((a, b) => b.r - a.r);
  let left = 100 - floors.reduce((a, b) => a + b, 0);
  const out = [...floors];
  for (const { i } of remainders) {
    if (left <= 0) break;
    out[i] += 1;
    left -= 1;
  }
  return out;
}
