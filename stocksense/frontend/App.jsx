import { useState, useMemo, useEffect, useRef } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import {
  Package, AlertTriangle, TrendingUp, IndianRupee, MessageCircle,
  Search, ChevronUp, ChevronDown, Bell, Wifi, Send, ArrowUpDown,
  CheckCircle2, Store, Sparkles, Filter, X, RefreshCw, Moon, Sun,
} from "lucide-react";

import {
  fetchStores,
  fetchForecast,
  fetchInventory,
  fetchStats,
  fetchMessages,
} from "./src/api";

const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const DAY_MULTIPLIERS = [0.9, 0.95, 1.0, 1.05, 1.15, 1.25, 1.05];

// ─── CSS (design tokens + dark mode) ─────────────────────────────────────────

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Light tokens ── */
.ss-root {
  --bg-page   : #F8F9FA;
  --bg-card   : #FFFFFF;
  --bg-nav    : #FFFFFF;
  --bg-row    : #FAFAFA;
  --bg-hover  : #F0FDF4;
  --bg-input  : #F9FAFB;
  --bg-badge  : #F3F4F6;
  --bg-chip   : #F0FDF4;
  --border    : #E5E7EB;
  --border-md : #D1D5DB;
  --border-chip:#BBF7D0;
  --txt-primary : #111827;
  --txt-secondary:#4B5563;
  --txt-muted  : #6B7280;
  --txt-faint  : #9CA3AF;
  --txt-chip   : #15803D;
  --txt-badge  : #6B7280;
  --shadow-card: 0 1px 3px rgba(0,0,0,.05);
  --shadow-lift: 0 10px 28px rgba(0,0,0,.09);
  --shadow-toast:0 8px 36px rgba(0,0,0,.22);
  --tbl-head   : #FAFAFA;
  --sort-btn-bg: #F3F4F6;
  --search-bg  : #F9FAFB;
  --wa-chat-bg : #E5DDD5;
  --wa-mine    : #DCF8C6;
  --wa-theirs  : #FFFFFF;
  --wa-input-bg: #EDEDED;
  --wa-mine-txt: #1a1a1a;
  --wa-theirs-txt:#1a1a1a;
  --scroll-thumb:#D1D5DB;

  /* accent colours stay same in both modes */
  --green      : #16A34A;
  --green-dark : #15803D;
  --green-hover: #14532D;
  --red        : #DC2626;
  --amber      : #D97706;
  --blue       : #1D4ED8;

  font-family:'Inter', system-ui, sans-serif;
  background: var(--bg-page);
  color: var(--txt-primary);
  min-height:100vh;
  transition: background .35s ease, color .35s ease;
}

/* ── Dark tokens ── */
.ss-root.dark {
  --bg-page   : #0F1117;
  --bg-card   : #1A1D27;
  --bg-nav    : #13151F;
  --bg-row    : #1E2130;
  --bg-hover  : #1A2E22;
  --bg-input  : #1E2130;
  --bg-badge  : #252836;
  --bg-chip   : #14261B;
  --border    : #2A2E3F;
  --border-md : #363A50;
  --border-chip: #1E4430;
  --txt-primary : #F1F3F9;
  --txt-secondary:#C4C9D8;
  --txt-muted  : #8B92A8;
  --txt-faint  : #5A6070;
  --txt-chip   : #4ADE80;
  --txt-badge  : #8B92A8;
  --shadow-card: 0 1px 6px rgba(0,0,0,.35);
  --shadow-lift: 0 10px 32px rgba(0,0,0,.45);
  --shadow-toast:0 8px 40px rgba(0,0,0,.55);
  --tbl-head   : #161921;
  --sort-btn-bg: #252836;
  --search-bg  : #1E2130;
  --wa-chat-bg : #0E1621;
  --wa-mine    : #054D2B;
  --wa-theirs  : #1F2430;
  --wa-input-bg: #101720;
  --wa-mine-txt: #E2F5E9;
  --wa-theirs-txt:#D4D9E8;
  --scroll-thumb:#363A50;
}

.ss-root *, .ss-root *::before, .ss-root *::after { box-sizing:border-box; margin:0; padding:0; }

/* ── Global colour transitions ── */
.ss-root .card,
.ss-root .nav-bar,
.ss-root .tab-bar,
.ss-root thead tr,
.ss-root .tbl-row,
.ss-root input,
.ss-root button { transition: background .3s ease, border-color .3s ease, color .3s ease, box-shadow .3s ease; }

/* ── Keyframes ── */
@keyframes ss-fadeUp  { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes ss-fadeIn  { from{opacity:0} to{opacity:1} }
@keyframes ss-rowIn   { from{opacity:0;transform:translateX(-6px)} to{opacity:1;transform:translateX(0)} }
@keyframes ss-msgPop  { from{opacity:0;transform:scale(.92) translateY(6px)} to{opacity:1;transform:scale(1) translateY(0)} }
@keyframes ss-toastIn { from{opacity:0;transform:translateX(-50%) translateY(24px) scale(.94)} to{opacity:1;transform:translateX(-50%) translateY(0) scale(1)} }
@keyframes ss-pulse   { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.45;transform:scale(.75)} }
@keyframes ss-spin    { to{transform:rotate(360deg)} }
@keyframes ss-toggleBg{ from{opacity:0} to{opacity:1} }
@keyframes ss-iconPop { 0%{transform:scale(.5) rotate(-30deg);opacity:0} 60%{transform:scale(1.2) rotate(5deg)} 100%{transform:scale(1) rotate(0deg);opacity:1} }
@keyframes ss-skeleton { 0%,100%{opacity:.45} 50%{opacity:.85} }
@keyframes pulse { 0%,100%{opacity:.6} 50%{opacity:1} }

.anim-fadeUp { animation:ss-fadeUp .48s cubic-bezier(.22,1,.36,1) both; }
.anim-fadeIn { animation:ss-fadeIn .3s ease both; }
.anim-rowIn  { animation:ss-rowIn  .28s cubic-bezier(.22,1,.36,1) both; }
.anim-msgPop { animation:ss-msgPop .32s cubic-bezier(.22,1,.36,1) both; }
.pulse-dot   { animation:ss-pulse 2.2s ease-in-out infinite; }
.icon-pop    { animation:ss-iconPop .38s cubic-bezier(.22,1,.36,1) both; }

.d-1{animation-delay:.04s} .d-2{animation-delay:.09s} .d-3{animation-delay:.13s}
.d-4{animation-delay:.18s} .d-5{animation-delay:.24s} .d-6{animation-delay:.30s}
.d-7{animation-delay:.36s} .d-8{animation-delay:.42s}

/* ── Card ── */
.card {
  background:var(--bg-card); border:1px solid var(--border);
  border-radius:18px; box-shadow:var(--shadow-card); overflow:hidden;
}
.card-lift { transition:transform .22s cubic-bezier(.22,1,.36,1), box-shadow .22s ease, background .3s; }
.card-lift:hover { transform:translateY(-3px); box-shadow:var(--shadow-lift); }

/* ── Nav & tabs ── */
.nav-bar { background:var(--bg-nav); border-bottom:1px solid var(--border); position:sticky; top:0; z-index:40; }
.tab-bar { background:var(--bg-nav); border-bottom:1px solid var(--border); }

.tab-btn {
  position:relative; display:inline-flex; align-items:center; gap:7px;
  height:48px; padding:0 2px; border:none; background:none; cursor:pointer;
  font-size:13.5px; font-weight:600; color:var(--txt-muted);
  font-family:inherit; transition:color .18s;
}
.tab-btn::after {
  content:''; position:absolute; bottom:0; left:-2px; right:-2px; height:2.5px;
  background:var(--green); border-radius:2px 2px 0 0;
  transform:scaleX(0); transform-origin:center;
  transition:transform .25s cubic-bezier(.22,1,.36,1);
}
.tab-btn.active { color:var(--green); }
.tab-btn.active::after { transform:scaleX(1); }
.tab-btn:not(.active):hover { color:var(--txt-secondary); }

/* ── Table ── */
.tbl-row { border-top:1px solid var(--border); }
.tbl-row:hover { background:var(--bg-hover); }
.sort-th { cursor:pointer; user-select:none; transition:color .13s; }
.sort-th:hover { color:var(--txt-primary) !important; }

/* ── Pill filters ── */
.pill {
  display:inline-flex; align-items:center; padding:5px 14px;
  border-radius:999px; border:1.5px solid transparent;
  font-size:12px; font-weight:700; cursor:pointer; white-space:nowrap;
  font-family:inherit; transition:all .18s cubic-bezier(.22,1,.36,1);
}
.pill.on  { background:var(--green); color:#fff; box-shadow:0 3px 10px rgba(22,163,74,.35); }
.pill.off { background:var(--bg-badge); color:var(--txt-muted); }
.pill.off:hover { background:var(--border); color:var(--txt-secondary); }

/* ── Buttons ── */
.btn-order {
  display:inline-flex; align-items:center; gap:6px;
  background:var(--green); color:#fff; border:none; border-radius:10px;
  font-size:12px; font-weight:700; padding:7px 13px; cursor:pointer;
  font-family:inherit; transition:background .15s, transform .1s, box-shadow .15s;
}
.btn-order:hover  { background:var(--green-dark); box-shadow:0 4px 14px rgba(22,163,74,.38); }
.btn-order:active { transform:scale(.95); }

/* ── Dark-mode toggle ── */
.dm-toggle {
  width:44px; height:26px; border-radius:999px; border:none; cursor:pointer; padding:0;
  display:flex; align-items:center; padding:3px;
  transition:background .3s ease;
  position:relative; overflow:hidden;
}
.dm-toggle.light { background:#E5E7EB; }
.dm-toggle.dark  { background:#4ADE80; }
.dm-toggle-knob {
  width:20px; height:20px; border-radius:50%; background:#fff;
  display:flex; align-items:center; justify-content:center;
  transition:transform .3s cubic-bezier(.22,1,.36,1), background .3s;
  flex-shrink:0; box-shadow:0 1px 4px rgba(0,0,0,.25);
}
.dm-toggle.dark .dm-toggle-knob { transform:translateX(18px); background:#052e16; }

/* ── Search ── */
.search-box {
  width:100%; padding:9px 12px 9px 38px;
  background:var(--search-bg); border:1.5px solid var(--border);
  border-radius:12px; font-size:13.5px; color:var(--txt-primary);
  outline:none; font-family:inherit;
  transition:border-color .18s, box-shadow .18s, background .3s;
}
.search-box::placeholder { color:var(--txt-faint); }
.search-box:focus { border-color:var(--green); box-shadow:0 0 0 3px rgba(22,163,74,.13); }

/* ── Logo ring ── */
.logo-ring {
  width:34px; height:34px; border-radius:10px; flex-shrink:0;
  background:linear-gradient(140deg,#22C55E 0%,#15803D 100%);
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 2px 8px rgba(22,163,74,.4);
}

/* ── Scrollbar ── */
.ss-root ::-webkit-scrollbar { width:5px; height:5px; }
.ss-root ::-webkit-scrollbar-track { background:transparent; }
.ss-root ::-webkit-scrollbar-thumb { background:var(--scroll-thumb); border-radius:10px; }

/* ── Notification badge ── */
.notif-border { border-color:var(--bg-nav) !important; }

/* ── Skeletons ── */
.skeleton {
  background:var(--bg-row);
  border:1px solid var(--border);
  border-radius:18px;
  animation:ss-skeleton 1.4s ease-in-out infinite;
}
`;

function Styles() {
  return <style dangerouslySetInnerHTML={{ __html: CSS }} />;
}

// ─── Logo ─────────────────────────────────────────────────────────────────────

function Logo() {
  return (
    <div className="logo-ring">
      <svg width="21" height="21" viewBox="0 0 21 21" fill="none">
        <rect x="1.5" y="13" width="4" height="6.5" rx="1.2" fill="rgba(255,255,255,.5)" />
        <rect x="8.5" y="9" width="4" height="10.5" rx="1.2" fill="rgba(255,255,255,.78)" />
        <rect x="15.5" y="4.5" width="4" height="15" rx="1.2" fill="#fff" />
        <path d="M3.5 12.5 L10.5 7.5 L17.5 4" stroke="rgba(255,255,255,.88)" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="17.5" cy="4" r="1.7" fill="rgba(255,255,255,.88)" />
      </svg>
    </div>
  );
}

// ─── Dark Mode Toggle ─────────────────────────────────────────────────────────

function DarkToggle({ dark, onToggle }) {
  return (
    <button
      className={`dm-toggle ${dark ? "dark" : "light"}`}
      onClick={onToggle}
      title={dark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label="Toggle dark mode"
    >
      <div className="dm-toggle-knob">
        {dark
          ? <Moon key="moon" size={11} color="#4ADE80" className="icon-pop" />
          : <Sun key="sun" size={11} color="#F59E0B" className="icon-pop" />
        }
      </div>
    </button>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

// Returns inline-style objects using CSS vars so they react to dark mode automatically
const T = {
  primary: { color: "var(--txt-primary)" },
  secondary: { color: "var(--txt-secondary)" },
  muted: { color: "var(--txt-muted)" },
  faint: { color: "var(--txt-faint)" },
  green: { color: "var(--green)" },
};

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function inventoryStatus(stock, avgDaily) {
  const safeStock = Number(stock) || 0;
  const safeAvg = Number(avgDaily) || 0;
  const daysLeft = safeAvg > 0 ? safeStock / safeAvg : safeStock > 0 ? 99 : 0;
  if (daysLeft <= 3) return "Critical";
  if (daysLeft <= 7) return "Low";
  return "Good";
}

// ─── Status Pill ──────────────────────────────────────────────────────────────

function StatusPill({ status, dark }) {
  // Light & dark variants for each status
  const map = {
    "Order now": {
      l: { bg: "#FEF2F2", color: "#DC2626", border: "1px solid #FCA5A5" },
      d: { bg: "#2D1212", color: "#F87171", border: "1px solid #7F1D1D" }
    },
    "Order soon": {
      l: { bg: "#FFFBEB", color: "#D97706", border: "1px solid #FCD34D" },
      d: { bg: "#27200A", color: "#FCD34D", border: "1px solid #78350F" }
    },
    "Sufficient": {
      l: { bg: "#F0FDF4", color: "#16A34A", border: "1px solid #86EFAC" },
      d: { bg: "#0A2016", color: "#4ADE80", border: "1px solid #14532D" }
    },
    "Critical": {
      l: { bg: "#FEF2F2", color: "#DC2626", border: "1px solid #FCA5A5" },
      d: { bg: "#2D1212", color: "#F87171", border: "1px solid #7F1D1D" }
    },
    "Low": {
      l: { bg: "#FFFBEB", color: "#D97706", border: "1px solid #FCD34D" },
      d: { bg: "#27200A", color: "#FCD34D", border: "1px solid #78350F" }
    },
    "Good": {
      l: { bg: "#F0FDF4", color: "#16A34A", border: "1px solid #86EFAC" },
      d: { bg: "#0A2016", color: "#4ADE80", border: "1px solid #14532D" }
    },
  };
  const s = (map[status] || map["Sufficient"])[dark ? "d" : "l"];
  return (
    <span style={{ display: "inline-flex", alignItems: "center", padding: "3px 10px", borderRadius: 999, fontSize: 11, fontWeight: 700, lineHeight: "18px", whiteSpace: "nowrap", background: s.bg, color: s.color, border: s.border, transition: "background .3s, color .3s, border-color .3s" }}>
      {status}
    </span>
  );
}

// ─── Toast ────────────────────────────────────────────────────────────────────

function Toast({ msg, onClose }) {
  useEffect(() => { const t = setTimeout(onClose, 3400); return () => clearTimeout(t); }, [onClose]);
  return (
    <div style={{
      position: "fixed", bottom: 28, left: "50%", zIndex: 9999,
      display: "flex", alignItems: "center", gap: 10,
      background: "#111827", color: "#fff",
      padding: "11px 18px 11px 14px", borderRadius: 16,
      boxShadow: "0 8px 36px rgba(0,0,0,.38)",
      fontSize: 13.5, fontWeight: 600, whiteSpace: "nowrap",
      animation: "ss-toastIn .42s cubic-bezier(.22,1,.36,1) both",
    }}>
      <CheckCircle2 size={16} color="#4ADE80" style={{ flexShrink: 0 }} />
      {msg}
      <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", padding: "0 0 0 6px", color: "#9CA3AF", display: "flex", lineHeight: 1 }}>
        <X size={13} />
      </button>
    </div>
  );
}

// ─── Stat Card ────────────────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, iconBg, iconBgDark, iconColor, valColor, valColorDark, sub, delay = 0, dark }) {
  const [show, setShow] = useState(false);
  useEffect(() => { const t = setTimeout(() => setShow(true), delay); return () => clearTimeout(t); }, [delay]);
  return (
    <div className="card card-lift"
      style={{
        padding: 20, display: "flex", alignItems: "flex-start", gap: 15,
        opacity: show ? 1 : 0, animation: show ? `ss-fadeUp .48s cubic-bezier(.22,1,.36,1) both` : "none"
      }}>
      <div style={{ background: dark ? iconBgDark : iconBg, borderRadius: 14, padding: 11, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, transition: "background .3s" }}>
        <Icon size={22} color={iconColor} />
      </div>
      <div>
        <p style={{ margin: 0, fontSize: 11.5, fontWeight: 700, letterSpacing: ".02em", marginBottom: 4, ...T.faint }}>{label}</p>
        <p style={{ margin: 0, fontSize: 29, fontWeight: 900, lineHeight: 1, letterSpacing: "-.5px", color: dark ? valColorDark : valColor, transition: "color .3s" }}>{value}</p>
        {sub && <p style={{ margin: "5px 0 0", fontSize: 11.5, fontWeight: 500, ...T.faint }}>{sub}</p>}
      </div>
    </div>
  );
}

// ─── Chart Tooltip ────────────────────────────────────────────────────────────

function ChartTip({ active, payload, label, dark }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: dark ? "#1E2130" : "#fff", border: `1px solid ${dark ? "#2A2E3F" : "#E5E7EB"}`, borderRadius: 12, padding: "10px 14px", boxShadow: dark ? "0 6px 24px rgba(0,0,0,.5)" : "0 6px 20px rgba(0,0,0,.1)", fontSize: 12 }}>
      <p style={{ margin: "0 0 6px", fontWeight: 800, fontSize: 13, color: dark ? "#F1F3F9" : "#374151" }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ margin: "2px 0", fontWeight: 600, color: p.color }}>
          {p.name} — <span style={{ color: dark ? "#C4C9D8" : "#1F2937" }}>{p.value} units</span>
        </p>
      ))}
    </div>
  );
}

// ─── Reorder Table ────────────────────────────────────────────────────────────

function ReorderTable({ rows, onOrder, dark, loading }) {
  if (loading) {
    return <div className="card skeleton" style={{ height: 376, animation: "pulse 1.5s ease-in-out infinite" }} />;
  }
  return (
    <div className="card anim-fadeUp d-5">
      <div style={{ padding: "18px 20px 13px", borderBottom: `1px solid var(--border)`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 14.5, fontWeight: 800, ...T.primary }}>Reorder Recommendations</h2>
          <p style={{ margin: "2px 0 0", fontSize: 12, fontWeight: 500, ...T.faint }}>AI forecast · next 7 days</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 5, background: "var(--bg-chip)", borderRadius: 9, padding: "5px 11px", border: "1px solid var(--border-chip)", transition: "background .3s, border-color .3s" }}>
          <Sparkles size={12} color="var(--green)" />
          <span style={{ fontSize: 11, fontWeight: 700, color: "var(--txt-chip)", transition: "color .3s" }}>Live AI</span>
        </div>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "var(--tbl-head)", transition: "background .3s" }}>
              {["Product", "Stock Left", "7-Day Forecast", "Reorder Qty", "Status", ""].map(h => (
                <th key={h} style={{ padding: "9px 16px", textAlign: "left", fontSize: 10.5, fontWeight: 800, letterSpacing: ".06em", textTransform: "uppercase", whiteSpace: "nowrap", ...T.faint }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.id} className={`tbl-row anim-rowIn d-${Math.min(i + 1, 8)}`}>
                <td style={{ padding: "11px 16px", fontWeight: 700, whiteSpace: "nowrap", ...T.primary }}>{row.product}</td>
                <td style={{ padding: "11px 16px", fontWeight: row.stock <= 5 ? 700 : 400, color: row.stock <= 5 ? "var(--red)" : "var(--txt-secondary)", transition: "color .3s" }}>{row.stock} units</td>
                <td style={{ padding: "11px 16px", ...T.muted }}>{row.forecast} units</td>
                <td style={{ padding: "11px 16px", fontWeight: 800, ...T.primary }}>
                  {row.reorderQty > 0 ? row.reorderQty : <span style={{ ...T.faint }}>—</span>}
                </td>
                <td style={{ padding: "11px 16px" }}><StatusPill status={row.status} dark={dark} /></td>
                <td style={{ padding: "11px 16px" }}>
                  {row.status !== "Sufficient" && (
                    <button className="btn-order" onClick={() => onOrder(row)}>
                      <MessageCircle size={12} /> Order
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── SKU Chart ────────────────────────────────────────────────────────────────

function SKUChart({ dark, chartData, seriesLabels, loading }) {
  if (loading) {
    return <div className="card skeleton" style={{ height: 326, animation: "pulse 1.5s ease-in-out infinite" }} />;
  }
  const tip = (props) => <ChartTip {...props} dark={dark} />;
  return (
    <div className="card anim-fadeUp d-6" style={{ display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "18px 20px 13px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 14.5, fontWeight: 800, ...T.primary }}>Top SKUs This Week</h2>
          <p style={{ margin: "2px 0 0", fontSize: 12, fontWeight: 500, ...T.faint }}>Units sold per day</p>
        </div>
        <TrendingUp size={16} color="var(--green)" />
      </div>
      <div style={{ padding: "16px 10px 8px", flex: 1 }}>
        <ResponsiveContainer width="100%" height={228}>
          <BarChart data={chartData} barSize={9} barGap={4} barCategoryGap="28%">
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: dark ? "#5A6070" : "#9CA3AF", fontWeight: 700 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: dark ? "#5A6070" : "#9CA3AF" }} axisLine={false} tickLine={false} width={22} />
            <Tooltip content={tip} cursor={{ fill: dark ? "rgba(255,255,255,.04)" : "#F9FAFB", radius: 6 }} />
            <Legend formatter={v => <span style={{ fontSize: 11, color: dark ? "#8B92A8" : "#6B7280", fontWeight: 700 }}>{v}</span>} iconType="circle" iconSize={7} />
            <Bar dataKey="sku1" name={seriesLabels[0]} fill="#16A34A" radius={[5, 5, 0, 0]} />
            <Bar dataKey="sku2" name={seriesLabels[1]} fill="#3B82F6" radius={[5, 5, 0, 0]} />
            <Bar dataKey="sku3" name={seriesLabels[2]} fill="#F59E0B" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ─── WhatsApp Feed ────────────────────────────────────────────────────────────

function WhatsAppFeed({ dark, messages, loading }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  useEffect(() => { setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 120); }, [messages]);

  if (loading) {
    return <div className="card skeleton" style={{ height: "calc(100vh - 196px)", minHeight: 520, animation: "pulse 1.5s ease-in-out infinite" }} />;
  }

  return (
    <div className="anim-fadeIn" style={{ maxWidth: 620, margin: "0 auto" }}>
      <div className="card" style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 196px)", minHeight: 520 }}>
        {/* Header */}
        <div style={{ background: dark ? "#0A1929" : "#075E54", padding: "13px 18px", display: "flex", alignItems: "center", gap: 13, transition: "background .35s" }}>
          <div style={{ width: 42, height: 42, borderRadius: "50%", background: "rgba(255,255,255,.15)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
            <Store size={20} color="#fff" />
          </div>
          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, color: "#fff", fontWeight: 800, fontSize: 14.5 }}>StockSense Assistant</p>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 2 }}>
              <span className="pulse-dot" style={{ width: 7, height: 7, borderRadius: "50%", background: "#4ADE80", display: "inline-block" }} />
              <span style={{ color: "rgba(255,255,255,.65)", fontSize: 11.5, fontWeight: 500 }}>Connected · Sales bot active</span>
            </div>
          </div>
          <Wifi size={16} color="rgba(255,255,255,.5)" />
        </div>

        {/* Messages */}
        <div style={{
          flex: 1, overflowY: "auto", padding: "14px 14px 6px", background: "var(--wa-chat-bg)",
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23c8b8a2' fill-opacity='${dark ? 0.06 : 0.18}'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E")`,
          transition: "background .35s"
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
            {messages.map((msg, i) => (
              <div key={msg.id || i} className="anim-msgPop" style={{ display: "flex", justifyContent: msg.from === "owner" ? "flex-end" : "flex-start", animationDelay: `${i * 0.045}s` }}>
                <div style={{
                  maxWidth: "80%",
                  background: msg.from === "owner" ? "var(--wa-mine)" : "var(--wa-theirs)",
                  borderRadius: msg.from === "owner" ? "18px 4px 18px 18px" : "4px 18px 18px 18px",
                  padding: "9px 13px",
                  boxShadow: dark ? "0 1px 4px rgba(0,0,0,.4)" : "0 1px 4px rgba(0,0,0,.1)",
                  fontSize: 13.5, lineHeight: 1.55,
                  color: msg.from === "owner" ? "var(--wa-mine-txt)" : "var(--wa-theirs-txt)",
                  whiteSpace: "pre-line", transition: "background .35s, color .35s",
                }}>
                  {msg.from === "system" && (
                    <p style={{ margin: "0 0 3px", color: dark ? "#4ADE80" : "#075E54", fontWeight: 800, fontSize: 11, transition: "color .3s" }}>StockSense</p>
                  )}
                  {msg.text}
                  <p style={{ margin: "4px 0 0", textAlign: "right", fontSize: 10.5, fontWeight: 500, color: dark ? "#4A5568" : "#94A3B8" }}>{msg.time}</p>
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Input */}
        <div style={{ background: "var(--wa-input-bg)", padding: "10px 12px", display: "flex", alignItems: "center", gap: 10, borderTop: `1px solid var(--border)`, transition: "background .35s, border-color .3s" }}>
          <input value={input} onChange={e => setInput(e.target.value)}
            placeholder='Try: "Sold 3 Toor Dal, 2 Maggi"'
            style={{ flex: 1, background: dark ? "#1E2130" : "#fff", border: `1px solid var(--border)`, borderRadius: 24, padding: "9px 16px", fontSize: 13.5, color: "var(--txt-primary)", outline: "none", fontFamily: "inherit", transition: "background .3s, border-color .3s, color .3s" }}
          />
          <button style={{ width: 40, height: 40, borderRadius: "50%", background: "#25D366", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, transition: "background .15s, transform .1s" }}
            onMouseEnter={e => e.currentTarget.style.background = "#1EBD5A"}
            onMouseLeave={e => e.currentTarget.style.background = "#25D366"}
            onMouseDown={e => e.currentTarget.style.transform = "scale(.92)"}
            onMouseUp={e => e.currentTarget.style.transform = "scale(1)"}>
            <Send size={16} color="#fff" />
          </button>
        </div>
      </div>
      <p style={{ textAlign: "center", fontSize: 12, fontWeight: 500, marginTop: 12, ...T.faint }}>
        Type sales in plain Hindi or English — StockSense understands both.
      </p>
    </div>
  );
}

// ─── Inventory Table ──────────────────────────────────────────────────────────

function InventoryTable({ dark, items, categories, loading }) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [sortKey, setSortKey] = useState("product");
  const [sortDir, setSortDir] = useState("asc");

  function toggleSort(key) {
    if (sortKey === key) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortKey(key); setSortDir("asc"); }
  }
  function days(s, a) { return a === 0 ? "∞" : Math.round(s / a); }

  const rows = useMemo(() => {
    let r = items;
    if (category !== "All") r = r.filter(x => x.category === category);
    if (search) r = r.filter(x => x.product.toLowerCase().includes(search.toLowerCase()));
    return [...r].sort((a, b) => {
      let av = a[sortKey], bv = b[sortKey];
      if (typeof av === "string") { av = av.toLowerCase(); bv = bv.toLowerCase(); }
      return sortDir === "asc" ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
    });
  }, [items, search, category, sortKey, sortDir]);

  function SortIco({ col }) {
    if (sortKey !== col) return <ArrowUpDown size={11} color="var(--border-md)" />;
    return sortDir === "asc"
      ? <ChevronUp size={11} color="var(--green)" />
      : <ChevronDown size={11} color="var(--green)" />;
  }

  const COLS = [
    { k: "product", l: "Product", nosort: false },
    { k: "category", l: "Category", nosort: false },
    { k: "unit", l: "Unit", nosort: true },
    { k: "stock", l: "Stock", nosort: false },
    { k: "avgDaily", l: "Avg Daily", nosort: false },
    { k: "days", l: "Days Left", nosort: true },
    { k: "status", l: "Status", nosort: true },
  ];

  if (loading) {
    return (
      <div className="anim-fadeIn" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        <div className="card skeleton" style={{ height: 110, animation: "pulse 1.5s ease-in-out infinite" }} />
        <div className="card skeleton" style={{ height: 360, animation: "pulse 1.5s ease-in-out infinite" }} />
      </div>
    );
  }

  return (
    <div className="anim-fadeIn" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div className="card" style={{ padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ position: "relative" }}>
          <Search size={14} color="var(--txt-faint)" style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
          <input className="search-box" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search products…" />
        </div>
        <div style={{ display: "flex", gap: 7, flexWrap: "wrap" }}>
          {categories.map(c => (
            <button key={c} className={`pill ${category === c ? "on" : "off"}`} onClick={() => setCategory(c)}>{c}</button>
          ))}
        </div>
      </div>

      <div className="card">
        <div style={{ padding: "10px 18px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <p style={{ margin: 0, fontSize: 12, fontWeight: 800, ...T.faint }}>{rows.length} ITEMS</p>
          <div style={{ display: "flex", alignItems: "center", gap: 5, ...T.faint }}>
            <Filter size={12} /><span style={{ fontSize: 11, fontWeight: 600 }}>Click header to sort</span>
          </div>
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "var(--tbl-head)", transition: "background .3s" }}>
                {COLS.map(col => (
                  <th key={col.k} className={col.nosort ? "" : "sort-th"}
                    onClick={() => !col.nosort && toggleSort(col.k)}
                    style={{ padding: "9px 16px", textAlign: "left", fontSize: 10.5, fontWeight: 800, letterSpacing: ".06em", textTransform: "uppercase", whiteSpace: "nowrap", ...T.faint }}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
                      {col.l}{!col.nosort && <SortIco col={col.k} />}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => {
                const d = days(row.stock, row.avgDaily);
                const dn = typeof d === "number" ? d : 999;
                return (
                  <tr key={row.id} className="tbl-row anim-rowIn" style={{ animationDelay: `${i * 0.028}s` }}>
                    <td style={{ padding: "10px 16px", fontWeight: 700, whiteSpace: "nowrap", ...T.primary }}>{row.product}</td>
                    <td style={{ padding: "10px 16px" }}>
                      <span style={{ background: "var(--bg-badge)", padding: "2px 9px", borderRadius: 7, fontSize: 11, fontWeight: 700, color: "var(--txt-badge)", transition: "background .3s, color .3s" }}>{row.category}</span>
                    </td>
                    <td style={{ padding: "10px 16px", fontWeight: 500, ...T.faint }}>{row.unit}</td>
                    <td style={{ padding: "10px 16px", fontWeight: 800, color: row.stock <= 5 ? "var(--red)" : "var(--txt-secondary)", transition: "color .3s" }}>{row.stock}</td>
                    <td style={{ padding: "10px 16px", ...T.muted }}>{row.avgDaily}/day</td>
                    <td style={{
                      padding: "10px 16px", fontWeight: 800,
                      color: dn <= 3 ? "var(--red)" : dn <= 7 ? "var(--amber)" : "var(--txt-secondary)",
                      transition: "color .3s"
                    }}>
                      {d}{d !== "∞" && <span style={{ fontSize: 11, fontWeight: 400, ...T.faint }}> d</span>}
                    </td>
                    <td style={{ padding: "10px 16px" }}><StatusPill status={row.status} dark={dark} /></td>
                  </tr>
                );
              })}
              {rows.length === 0 && (
                <tr><td colSpan={7} style={{ padding: "44px 16px", textAlign: "center", fontSize: 13, ...T.faint }}>No products match your search.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────

const TABS = [
  { id: "overview", label: "Overview", Icon: TrendingUp },
  { id: "whatsapp", label: "WhatsApp", Icon: MessageCircle },
  { id: "inventory", label: "Inventory", Icon: Package },
];

export default function StockSense() {
  const [tab, setTab] = useState("overview");
  const [dark, setDark] = useState(false);
  const [toast, setToast] = useState(null);

  const [storeId, setStoreId] = useState(1);
  const [stores, setStores] = useState([]);
  const [stats, setStats] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function loadAll() {
      setLoading(true);
      const [s, st, f, inv, msg] = await Promise.all([
        fetchStores(),
        fetchStats(storeId),
        fetchForecast(storeId),
        fetchInventory(storeId),
        fetchMessages(storeId),
      ]);

      if (cancelled) return;

      const firstError = [s, st, f, inv, msg].find(r => r.error);
      setError(firstError ? "Could not connect to server. Is the backend running?" : null);
      setStores(s.data || []);
      setStats(st.data || {});
      setForecast(f.data || []);
      setInventory(inv.data || []);
      setMessages(msg.data || []);
      setLoading(false);
    }

    loadAll();
    return () => { cancelled = true; };
  }, [storeId]);

  const selectedStore = useMemo(
    () => stores.find(s => s.id === storeId),
    [stores, storeId]
  );

  const inventoryByName = useMemo(() => {
    const map = new Map();
    inventory.forEach(item => {
      if (item.sku_name) {
        map.set(item.sku_name.toLowerCase(), item);
      }
    });
    return map;
  }, [inventory]);

  const reorderRows = useMemo(() => {
    return forecast.map((item, index) => {
      const key = (item.sku_name || "").toLowerCase();
      const inv = inventoryByName.get(key);
      return {
        id: item.sku_name || index,
        product: item.sku_name || "Unknown",
        stock: Number(inv?.current_stock ?? 0),
        forecast: Number(item.predicted_qty ?? 0),
        reorderQty: Number(item.reorder_qty ?? 0),
        status: item.status || "Sufficient",
        supplier: selectedStore ? `${selectedStore.name} Supplier` : "Supplier",
      };
    });
  }, [forecast, inventoryByName, selectedStore]);

  const inventoryRows = useMemo(() => {
    return inventory.map((item, index) => {
      const stock = Number(item.current_stock ?? 0);
      const avgDaily = Number(item.avg_daily_sales ?? 0);
      return {
        id: item.sku_id ?? index,
        product: item.sku_name || "Unknown",
        category: item.category || "General",
        unit: item.unit || "units",
        stock,
        avgDaily,
        status: inventoryStatus(stock, avgDaily),
      };
    });
  }, [inventory]);

  const inventoryCategories = useMemo(() => {
    const set = new Set(inventoryRows.map(row => row.category));
    return ["All", ...Array.from(set)];
  }, [inventoryRows]);

  const chartSeries = useMemo(() => {
    const sorted = [...forecast].sort(
      (a, b) => Number(b.predicted_qty ?? 0) - Number(a.predicted_qty ?? 0)
    );
    const top = sorted.slice(0, 3);
    const labels = ["SKU 1", "SKU 2", "SKU 3"].map(
      (label, index) => top[index]?.sku_name || label
    );
    const baseSales = [0, 0, 0].map((_, index) => {
      const item = top[index];
      if (!item) return 0;
      const inv = inventoryByName.get((item.sku_name || "").toLowerCase());
      const avg = Number(inv?.avg_daily_sales ?? 0);
      if (avg > 0) return avg;
      const predicted = Number(item.predicted_qty ?? 0);
      return predicted > 0 ? predicted / 7 : 0;
    });

    const data = DAY_LABELS.map((day, dayIndex) => ({
      day,
      sku1: Math.round(baseSales[0] * DAY_MULTIPLIERS[dayIndex]),
      sku2: Math.round(baseSales[1] * DAY_MULTIPLIERS[dayIndex]),
      sku3: Math.round(baseSales[2] * DAY_MULTIPLIERS[dayIndex]),
    }));

    return { data, labels };
  }, [forecast, inventoryByName]);

  const chatMessages = useMemo(() => {
    return messages.map((m, index) => ({
      id: m.id ?? index,
      from: m.from === "system" ? "system" : "owner",
      text: m.text || "",
      time: formatTime(m.time),
    }));
  }, [messages]);

  function handleOrder(row) {
    setToast(`WhatsApp sent to ${row.supplier} ✓`);
  }

  // Nav button styles that need JS to react to dark mode
  const navBtnStyle = {
    position: "relative", width: 36, height: 36, borderRadius: 10,
    border: `1.5px solid var(--border)`, background: "var(--bg-card)",
    cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
  };

  return (
    <div className={`ss-root${dark ? " dark" : ""}`}>
      <Styles />

      {error && (
        <div style={{
          maxWidth: 1300,
          margin: "12px auto 0",
          padding: "10px 16px",
          background: "#FEE2E2",
          border: "1px solid #FCA5A5",
          color: "#991B1B",
          borderRadius: 12,
          fontSize: 13,
          fontWeight: 700,
          display:"flex",
          alignItems:"center",
          justifyContent:"space-between",
          gap:12,
        }}>
          <span>{error}</span>
          <button
            onClick={() => window.location.reload()}
            style={{
              background:"#991B1B",
              color:"#fff",
              border:"none",
              borderRadius:10,
              padding:"6px 12px",
              cursor:"pointer",
              fontSize:12,
              fontWeight:700,
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* ── Nav Bar ── */}
      <header className="nav-bar">
        <div style={{ maxWidth: 1300, margin: "0 auto", padding: "0 22px", height: 56, display: "flex", alignItems: "center", justifyContent: "space-between" }}>

          {/* Brand */}
          <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
            <Logo />
            <div style={{ lineHeight: 1.1 }}>
              <div style={{ fontWeight: 900, fontSize: 16.5, letterSpacing: "-.4px", ...T.primary }}>StockSense</div>
              <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: ".12em", ...T.faint }}>AI INVENTORY</div>
            </div>
            <div style={{ marginLeft: 8, background: "var(--bg-chip)", border: "1px solid var(--border-chip)", borderRadius: 9, padding: "3px 11px", display: "flex", alignItems: "center", gap: 6, transition: "background .3s, border-color .3s" }}>
              <Store size={11} color="var(--green)" />
              <select
                value={storeId}
                onChange={(e) => setStoreId(Number(e.target.value))}
                aria-label="Select store"
                style={{
                  border: "none",
                  background: "transparent",
                  color: "var(--txt-chip)",
                  fontSize: 11.5,
                  fontWeight: 700,
                  cursor: "pointer",
                  outline: "none",
                  fontFamily: "inherit",
                }}
              >
                {stores.length === 0 ? (
                  <option value={storeId}>Loading store…</option>
                ) : (
                  stores.map((store) => (
                    <option key={store.id} value={store.id}>
                      {store.name} · {store.pin_code}
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>

          {/* Right controls */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {/* WA status */}
            <div style={{ display: "flex", alignItems: "center", gap: 6, background: "var(--bg-chip)", border: "1px solid var(--border-chip)", padding: "5px 12px", borderRadius: 10, transition: "background .3s, border-color .3s" }}>
              <span className="pulse-dot" style={{ width: 7, height: 7, background: "#4ADE80", borderRadius: "50%", display: "inline-block" }} />
              <span style={{ fontSize: 11.5, fontWeight: 700, color: "var(--txt-chip)", transition: "color .3s" }}>WhatsApp</span>
            </div>
            {/* Sync label */}
            <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, fontWeight: 600, ...T.faint }}>
              <RefreshCw size={12} />
              <span>Synced 4:22 PM</span>
            </div>
            {/* Dark mode toggle */}
            <DarkToggle dark={dark} onToggle={() => setDark(d => !d)} />
            {/* Bell */}
            <button style={navBtnStyle}
              onMouseEnter={e => e.currentTarget.style.background = dark ? "#252836" : "#F9FAFB"}
              onMouseLeave={e => e.currentTarget.style.background = "var(--bg-card)"}>
              <Bell size={15} color="var(--txt-muted)" />
              <span style={{ position: "absolute", top: -5, right: -5, width: 18, height: 18, background: "#EF4444", borderRadius: "50%", color: "#fff", fontSize: 9, fontWeight: 900, display: "flex", alignItems: "center", justifyContent: "center", border: `2.5px solid var(--bg-nav)`, transition: "border-color .3s" }}>8</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── Tab Bar ── */}
      <div className="tab-bar">
        <div style={{ maxWidth: 1300, margin: "0 auto", padding: "0 22px", display: "flex", gap: 24 }}>
          {TABS.map(({ id, label, Icon }) => (
            <button key={id} className={`tab-btn${tab === id ? " active" : ""}`} onClick={() => setTab(id)}>
              <Icon size={14} />
              {label}
              {id === "whatsapp" && (
                <span style={{ background: "#EF4444", color: "#fff", fontSize: 9, fontWeight: 900, padding: "1px 5px", borderRadius: 999, lineHeight: "14px" }}>12</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* ── Content ── */}
      <main style={{ maxWidth: 1300, margin: "0 auto", padding: "24px 22px 48px" }}>

        {tab === "overview" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div className="anim-fadeIn" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <p style={{ margin: 0, fontSize: 12.5, fontWeight: 600, ...T.faint }}>
                {new Date().toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
                {" · Last synced: 4:22 PM"}
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, fontWeight: 700, color: "var(--green)" }}>
                <Sparkles size={12} />
                <span>AI forecast updated 4 mins ago</span>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(190px,1fr))", gap: 14 }}>
              {loading ? (
                [0, 1, 2, 3].map((i) => (
                  <div key={i} className="card skeleton" style={{ height: 92, animation: "pulse 1.5s ease-in-out infinite" }} />
                ))
              ) : (
                <>
                  <StatCard icon={AlertTriangle} label="Items to Reorder" value={stats?.reorder_count ?? 0} iconBg="#FEF2F2" iconBgDark="#2D1212" iconColor="#EF4444" valColor="#DC2626" valColorDark="#F87171" sub="Action needed today" delay={0} dark={dark} />
                  <StatCard icon={Package} label="Deadstock Risk" value={`${stats?.deadstock_count ?? 0} items`} iconBg="#FFFBEB" iconBgDark="#27200A" iconColor="#F59E0B" valColor="#D97706" valColorDark="#FCD34D" sub="Slow-moving items" delay={70} dark={dark} />
                  <StatCard icon={TrendingUp} label="Forecast Accuracy" value={`${stats?.forecast_accuracy ?? 0}%`} iconBg="#F0FDF4" iconBgDark="#0A2016" iconColor="#16A34A" valColor="#15803D" valColorDark="#4ADE80" sub="Last 30 days" delay={140} dark={dark} />
                  <StatCard icon={IndianRupee} label="This Week's Savings" value={`₹${stats?.savings_inr ?? 0}`} iconBg="#EFF6FF" iconBgDark="#0C1A2E" iconColor="#3B82F6" valColor="#1D4ED8" valColorDark="#60A5FA" sub="vs. manual ordering" delay={210} dark={dark} />
                </>
              )}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 14, alignItems: "start" }}>
              <ReorderTable rows={reorderRows} onOrder={handleOrder} dark={dark} loading={loading} />
              <SKUChart dark={dark} chartData={chartSeries.data} seriesLabels={chartSeries.labels} loading={loading} />
            </div>
          </div>
        )}

        {tab === "whatsapp" && <WhatsAppFeed dark={dark} messages={chatMessages} loading={loading} />}
        {tab === "inventory" && <InventoryTable dark={dark} items={inventoryRows} categories={inventoryCategories} loading={loading} />}
      </main>

      {toast && <Toast msg={toast} onClose={() => setToast(null)} />}
    </div>
  );
}
