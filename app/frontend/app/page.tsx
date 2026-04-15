export default function Home() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1>Travel Companion Platform</h1>
      <p>Connecting travelers. No one flies alone.</p>
      <div style={{ display: "flex", gap: "1rem", marginTop: "2rem" }}>
        <button
          style={{
            padding: "0.75rem 2rem",
            fontSize: "1rem",
            cursor: "pointer",
            border: "2px solid #0070f3",
            background: "#0070f3",
            color: "white",
            borderRadius: "8px",
          }}
        >
          Get Help
        </button>
        <button
          style={{
            padding: "0.75rem 2rem",
            fontSize: "1rem",
            cursor: "pointer",
            border: "2px solid #0070f3",
            background: "white",
            color: "#0070f3",
            borderRadius: "8px",
          }}
        >
          Offer Help
        </button>
      </div>
    </div>
  );
}
