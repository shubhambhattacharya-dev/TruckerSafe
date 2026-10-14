import { useEffect, useState } from "react";
import type { RoutePlanRequest } from "../types";

export interface FormState {
  origin: string;
  destination: string;
  date: string;
  time: string;
  loadLb: string;
  intervalMi: string;
}

function nextDay(): string {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const year = tomorrow.getFullYear();
  const month = String(tomorrow.getMonth() + 1).padStart(2, "0");
  const day = String(tomorrow.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export const DEFAULT_FORM: FormState = {
  origin: "Chicago, IL, USA",
  destination: "Denver, CO, USA",
  date: nextDay(),
  time: "08:00",
  loadLb: "40000",
  intervalMi: "25",
};

/** Local-time ISO with numeric offset, e.g. 2026-10-15T08:00:00-05:00. */
export function toDepartureIso(date: string, time: string): string {
  const d = new Date(`${date}T${time}:00`);
  if (Number.isNaN(d.getTime())) return `${date}T${time}:00Z`;
  const off = -d.getTimezoneOffset();
  const sign = off >= 0 ? "+" : "-";
  const abs = Math.abs(off);
  const hh = String(Math.floor(abs / 60)).padStart(2, "0");
  const mm = String(abs % 60).padStart(2, "0");
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:00${sign}${hh}:${mm}`;
}

export function toRequest(f: FormState): RoutePlanRequest {
  return {
    origin: f.origin,
    destination: f.destination,
    departure_time: toDepartureIso(f.date, f.time),
    load_lb: Number(f.loadLb),
    checkpoint_interval_miles: Number(f.intervalMi),
  };
}

function validate(f: FormState): Record<string, string> {
  const e: Record<string, string> = {};
  if (!f.origin.trim()) e.origin = "Origin is required.";
  if (!f.destination.trim()) e.destination = "Destination is required.";
  if (f.origin.trim() && f.origin.trim() === f.destination.trim())
    e.destination = "Destination must differ from origin.";
  const load = Number(f.loadLb);
  if (!Number.isFinite(load) || load < 1000 || load > 80000)
    e.loadLb = "Load must be between 1,000 and 80,000 lb.";
  if (!f.date) e.date = "Departure date is required.";
  if (!f.time) e.time = "Departure time is required.";
  return e;
}

interface Props {
  initial?: FormState;
  onSubmit: (f: FormState) => void;
  busy: boolean;
}

const PinIcon = ({ color }: { color: string }) => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill={color} aria-hidden>
    <path d="M12 2C8.1 2 5 5.1 5 9c0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3.1-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z" />
  </svg>
);

export default function RouteForm({ initial, onSubmit, busy }: Props) {
  const [form, setForm] = useState<FormState>(initial ?? DEFAULT_FORM);
  const [touched, setTouched] = useState(false);
  const errors = validate(form);

  // Loading a saved trip updates App state; keep the controlled fields in
  // sync instead of retaining the values from the component's first render.
  useEffect(() => {
    if (initial) setForm(initial);
  }, [initial]);

  const set = (k: keyof FormState) => (ev: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm({ ...form, [k]: ev.target.value });

  return (
    <form
      className="card form-card"
      onSubmit={(ev) => {
        ev.preventDefault();
        setTouched(true);
        if (Object.keys(errors).length === 0) onSubmit(form);
      }}
    >
      <h2>Plan Your Truck Route</h2>
      <p className="sub">Find the safest route based on weather, load weight and travel time.</p>

      <div className="field">
        <label><PinIcon color="#2563eb" /> Origin (A)</label>
        <input value={form.origin} onChange={set("origin")} placeholder="City, State" />
        {touched && errors.origin && <div className="error">{errors.origin}</div>}
      </div>
      <button type="button" className="swap-btn" title="Swap origin and destination"
        onClick={() => setForm({ ...form, origin: form.destination, destination: form.origin })}>
        ⇅
      </button>
      <div className="field">
        <label><PinIcon color="#ef4444" /> Destination (B)</label>
        <input value={form.destination} onChange={set("destination")} placeholder="City, State" />
        {touched && errors.destination && <div className="error">{errors.destination}</div>}
      </div>

      <div className="field">
        <label>📅 Departure Date &amp; Time</label>
        <div className="date-time-row">
          <input type="date" value={form.date} onChange={set("date")} />
          <input type="time" value={form.time} onChange={set("time")} />
        </div>
        {touched && (errors.date || errors.time) && (
          <div className="error">{errors.date || errors.time}</div>
        )}
      </div>

      <div className="field">
        <label>🚛 Truck Load Weight</label>
        <input value={form.loadLb} onChange={set("loadLb")} inputMode="numeric" />
        <span className="load-unit">lb</span>
        <div className="note">Heavier loads are more affected by strong wind.</div>
        {touched && errors.loadLb && <div className="error">{errors.loadLb}</div>}
      </div>

      <div className="field">
        <label>📍 Weather Checkpoints (miles) <span className="hint" title="Weather is sampled at every N miles along the route and matched to your estimated arrival time.">ⓘ</span></label>
        <select value={form.intervalMi} onChange={set("intervalMi")}>
          <option value="10">10 miles</option>
          <option value="25">25 miles</option>
          <option value="50">50 miles</option>
        </select>
        <div className="note">Get weather data every 10, 25, or 50 miles.</div>
      </div>

      <button className="btn-primary" type="submit" disabled={busy}>
        {busy ? "Analyzing routes…" : "➤ Find Safe Routes"}
      </button>
    </form>
  );
}
