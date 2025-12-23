import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL;

export default function App() {
  const [data, setData] = useState([]);
  const [clientName, setClientName] = useState("");
  const [year, setYear] = useState("");

  async function load() {
    const res = await fetch(`${API}/acceptance`);
    const json = await res.json();
    setData(json);
  }

  async function submit(e) {
    e.preventDefault();

    await fetch(`${API}/acceptance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_name: clientName,
        year: year
      }),
    });

    setClientName("");
    setYear("");
    load(); // refresh list
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>INTAX Audit Portal</h1>

      <h2>New Acceptance</h2>
      <form onSubmit={submit}>
        <input
          placeholder="Client name"
          value={clientName}
          onChange={(e) => setClientName(e.target.value)}
        />
        <input
          placeholder="Year"
          value={year}
          onChange={(e) => setYear(e.target.value)}
        />
        <button type="submit">Save</button>
      </form>

      <h2>Acceptance list</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
