/**
 * StockSense — Frontend Dashboard (Placeholder)
 *
 * NOTE: frontend.md was empty at the time of scaffold generation.
 * Replace this file with the actual JSX from frontend.md when available.
 */

import React from "react";

export default function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        color: "#e2e8f0",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
        📦 StockSense
      </h1>
      <p style={{ fontSize: "1.1rem", opacity: 0.7 }}>
        AI-powered inventory intelligence for kirana stores
      </p>
      <p
        style={{
          marginTop: "2rem",
          padding: "1rem 2rem",
          background: "rgba(255,255,255,0.05)",
          borderRadius: "12px",
          border: "1px solid rgba(255,255,255,0.1)",
        }}
      >
        Frontend scaffold — replace with frontend.md JSX when available.
      </p>
    </div>
  );
}
