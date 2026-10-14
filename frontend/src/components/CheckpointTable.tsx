import { useEffect, useMemo, useState } from "react";
import type { Checkpoint } from "../types";
import { BAND_COLORS, BAND_LABELS } from "../map/colors";
import { fmtEta } from "../util/format";

interface Props {
  checkpoints: Checkpoint[];
  intervalMi: number;
  allExpanded: boolean;
}

const PAGE_SIZE = 8;

export default function CheckpointTable({ checkpoints, intervalMi, allExpanded }: Props) {
  const [page, setPage] = useState(1);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const pageCount = Math.max(1, Math.ceil(checkpoints.length / PAGE_SIZE));
  useEffect(() => setPage(1), [checkpoints]);
  useEffect(() => {
    setExpanded(allExpanded ? new Set(checkpoints.map((c) => c.idx)) : new Set());
  }, [allExpanded, checkpoints]);

  const rows = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return checkpoints.slice(start, start + PAGE_SIZE);
  }, [checkpoints, page]);

  const toggle = (idx: number) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });

  return (
    <div className="table-wrap">
      <h4>Route Checkpoints (Every {intervalMi} Miles)</h4>
      <table>
        <thead>
          <tr>
            <th style={{ width: 34 }}>#</th>
            <th>Location</th>
            <th>Distance (mi)</th>
            <th>ETA (arrival)</th>
            <th>Wind (mph)</th>
            <th>Rain (in/hr)</th>
            <th>Snow (in/hr)</th>
            <th>Risk</th>
            <th style={{ width: 30 }} />
          </tr>
        </thead>
        <tbody>
          {rows.map((cp) => (
            <ExpandedRow key={cp.idx} cp={cp} open={expanded.has(cp.idx)} onToggle={() => toggle(cp.idx)} />
          ))}
        </tbody>
      </table>
      <div className="pager">
        <span className="of">
          Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, checkpoints.length)} of{" "}
          {checkpoints.length} checkpoints (every {intervalMi} miles)
        </span>
        <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>‹</button>
        {Array.from({ length: pageCount }, (_, i) => i + 1).map((p) => (
          <button key={p} className={p === page ? "on" : ""} onClick={() => setPage(p)}>{p}</button>
        ))}
        <button onClick={() => setPage((p) => Math.min(pageCount, p + 1))} disabled={page === pageCount}>›</button>
      </div>
    </div>
  );
}

function ExpandedRow({ cp, open, onToggle }: { cp: Checkpoint; open: boolean; onToggle: () => void }) {
  return (
    <>
      <tr className="expandable" onClick={onToggle}>
        <td>{cp.idx}</td>
        <td>{cp.location_name}</td>
        <td>{cp.distance_mi}</td>
        <td>{fmtEta(cp.eta)}</td>
        <td>{cp.wind_mph}</td>
        <td>{cp.rain_in_hr.toFixed(2)}</td>
        <td>{cp.snow_in_hr.toFixed(1)}</td>
        <td>
          <span className="chip-band" style={{ background: BAND_COLORS[cp.risk_band] }}>
            {BAND_LABELS[cp.risk_band]}
          </span>
        </td>
        <td><button className="chev" aria-label={`Toggle details for checkpoint ${cp.idx}`}>{open ? "⌄" : "›"}</button></td>
      </tr>
      {open && (
        <tr className="subrow">
          <td />
          <td colSpan={8}>
            Weather matched to this checkpoint's <b>estimated arrival time</b> ({fmtEta(cp.eta)}) ·
            position {cp.lat.toFixed(3)}, {cp.lon.toFixed(3)} · wind band from {cp.wind_mph} mph,
            rain band from {cp.rain_in_hr} in/hr, snow band from {cp.snow_in_hr} in/hr ·
            final risk <b style={{ color: BAND_COLORS[cp.risk_band] }}>{cp.risk_band}</b> (worst of the three, then load-rule upgrade).
          </td>
        </tr>
      )}
    </>
  );
}
