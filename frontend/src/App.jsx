import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL;

export default function App() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    async function run() {
      try {
        const res = await fetch(`${API}/acceptance`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        setData(json);
      } catch (e) {
        setErr(String(e));
      }
    }
    run();
  }, []);

  return (
    <div style={{ padding: 16, fontFamily: "Arial, sans-serif" }}>
      <h1>INTAX Audit Portal</h1>
      <div>API: {API}</div>

      {err ? (
        <p style={{ color: "red" }}>Error: {err}</p>
      ) : data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}
