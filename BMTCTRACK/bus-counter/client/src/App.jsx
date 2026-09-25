// src/App.jsx
import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:3001");
const MAX_CAPACITY = 40;

export default function App() {
  const [count, setCount]     = useState(0);
  const [history, setHistory] = useState([]);
  const [status, setStatus]   = useState("connecting");

  useEffect(() => {
    // Load initial state
    fetch("http://localhost:3001/passengers")
      .then(r => r.json())
      .then(d => setCount(d.count));

    fetch("http://localhost:3001/history")
      .then(r => r.json())
      .then(setHistory);

    // Live updates via WebSocket
    socket.on("connect",         () => setStatus("live"));
    socket.on("disconnect",      () => setStatus("disconnected"));
    socket.on("passengerUpdate", (data) => {
      setCount(data.count);
      setHistory(prev => [...prev.slice(-99), data]);
    });

    return () => socket.off("passengerUpdate");
  }, []);

  const pct      = Math.round((count / MAX_CAPACITY) * 100);
  const barColor = pct > 90 ? "#E24B4A" : pct > 70 ? "#EF9F27" : "#1D9E75";

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 600, margin: "2rem auto", padding: "0 1rem" }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: 20, fontWeight: 500, margin: 0 }}>Bus passenger counter</h1>
        <span style={{
          fontSize: 12, padding: "4px 10px", borderRadius: 20,
          background: status === "live" ? "#EAF3DE" : "#FCEBEB",
          color:      status === "live" ? "#3B6D11" : "#A32D2D"
        }}>
          {status === "live" ? "● Live" : "○ Disconnected"}
        </span>
      </div>

      {/* Count card */}
      <div style={{ background: "#f5f5f3", borderRadius: 12, padding: "1.5rem", marginBottom: "1rem", textAlign: "center" }}>
        <p style={{ fontSize: 13, color: "#888", margin: "0 0 8px" }}>Passengers on board</p>
        <p style={{ fontSize: 64, fontWeight: 500, margin: "0 0 16px", lineHeight: 1 }}>{count}</p>
        <p style={{ fontSize: 13, color: "#888", margin: "0 0 10px" }}>of {MAX_CAPACITY} capacity ({pct}%)</p>
        {/* Progress bar */}
        <div style={{ background: "#ddd", borderRadius: 6, height: 10, overflow: "hidden" }}>
          <div style={{ width: `${pct}%`, height: "100%", background: barColor, borderRadius: 6, transition: "width 0.4s, background 0.4s" }}/>
        </div>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: "1.5rem" }}>
        {[
          { label: "Status",    value: pct > 90 ? "Full" : pct > 70 ? "Busy" : "Normal" },
          { label: "IR events", value: history.length },
          { label: "Available", value: Math.max(0, MAX_CAPACITY - count) },
        ].map(({ label, value }) => (
          <div key={label} style={{ background: "#f5f5f3", borderRadius: 8, padding: "0.75rem 1rem" }}>
            <p style={{ fontSize: 12, color: "#888", margin: "0 0 4px" }}>{label}</p>
            <p style={{ fontSize: 20, fontWeight: 500, margin: 0 }}>{value}</p>
          </div>
        ))}
      </div>

      {/* Event log */}
      <div style={{ border: "0.5px solid #ddd", borderRadius: 10, overflow: "hidden" }}>
        <p style={{ fontSize: 13, fontWeight: 500, padding: "10px 14px", margin: 0, borderBottom: "0.5px solid #ddd" }}>
          Recent IR events
        </p>
        {history.length === 0 && (
          <p style={{ fontSize: 13, color: "#888", padding: "12px 14px", margin: 0 }}>Waiting for sensor data…</p>
        )}
        {[...history].reverse().slice(0, 8).map((h, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "8px 14px", borderBottom: "0.5px solid #eee", fontSize: 13 }}>
            <span>Count: <strong>{h.count}</strong></span>
            <span style={{ color: "#888" }}>{new Date(h.timestamp).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}