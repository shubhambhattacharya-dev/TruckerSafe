interface Props {
  page: "plan" | "trips";
  onNavigate: (p: "plan" | "trips") => void;
}

const TruckIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <rect x="1" y="6" width="13" height="10" rx="1.5" />
    <path d="M14 9h4l4 4v3h-8z" />
    <circle cx="6" cy="18.5" r="1.8" />
    <circle cx="18" cy="18.5" r="1.8" />
  </svg>
);

export default function TopBar({ page, onNavigate }: Props) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="logo"><TruckIcon /></div>
        <div>
          <h1>TruckerSafe</h1>
          <p>Weather-Aware Truck Routing</p>
        </div>
      </div>
      <nav aria-label="Main">
        <button className={page === "plan" ? "active" : ""} onClick={() => onNavigate("plan")}>
          Plan Route
        </button>
        <button className={page === "trips" ? "active" : ""} onClick={() => onNavigate("trips")}>
          My Trips
        </button>
      </nav>
      <div className="user">
        <button className="help-dot" title="Weather checkpoints are sampled every 10/25/50 miles and matched to your estimated arrival time at each one.">?</button>
        <div className="avatar" title="Signed in as Shubham">S</div>
        <span>Shubham</span>
      </div>
    </header>
  );
}
