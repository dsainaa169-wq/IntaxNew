import { useEffect, useMemo, useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL;

export default function App() {
  const [data, setData] = useState([]);
  const [companyName, setCompanyName] = useState("");
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [auditor, setAuditor] = useState("INTAX");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const apiLabel = useMemo(() => API || "(VITE_API_BASE_URL алга байна)", []);

  async function load() {
    if (!API) {
      setMsg("⚠️ VITE_API_BASE_URL алга байна (.env шалга)");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API}/acceptance`);
      const json = await res.json();
      setData(Array.isArray(json) ? json : []);
      setMsg("");
    } catch (e) {
      setMsg("LOAD error: " + String(e));
    } finally {
      setLoading(false);
    }
  }

  async function submit(e) {
    e.preventDefault();
    if (!API) {
      setMsg("⚠️ VITE_API_BASE_URL алга байна (.env шалга)");
      return;
    }

    setMsg("Saving...");
    try {
      const res = await fetch(`${API}/acceptance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: companyName,
          year: Number(year),
          auditor: auditor || "INTAX",
        }),
      });

      const text = await res.text();
      if (!res.ok) {
        setMsg(`POST failed: HTTP ${res.status} → ${text}`);
        return;
      }

      setMsg("Saved OK ✅");
      setCompanyName("");
      setYear(String(new Date().getFullYear()));
      setAuditor("INTAX");
      load();
    } catch (e) {
      setMsg("POST error: " + String(e));
    }
  }

  async function remove(id) {
    if (!API) {
      setMsg("⚠️ VITE_API_BASE_URL алга байна (.env шалга)");
      return;
    }
    const ok = confirm("Устгах уу?");
    if (!ok) return;

    setMsg("Deleting...");
    try {
      const res = await fetch(`${API}/acceptance/${id}`, {
        method: "DELETE",
      });

      const text = await res.text();
      if (!res.ok) {
        setMsg(`DELETE failed: HTTP ${res.status} → ${text}`);
        return;
      }

      setMsg("Deleted ✅");
      load();
    } catch (e) {
      setMsg("DELETE error: " + String(e));
    }
  }

  async function copyId(id) {
    try {
      await navigator.clipboard.writeText(id);
      setMsg("ID copied ✅");
    } catch (e) {
      setMsg("Copy failed: " + String(e));
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{ padding: 20, maxWidth: 900, margin: "0 auto" }}>
      <h1 style={{ marginBottom: 6 }}>INTAX Audit Portal</h1>

      <div style={{ marginBottom: 12 }}>
        <b>API:</b> {apiLabel}
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button onClick={load} disabled={loading}>
          {loading ? "Loading..." : "Reload"}
        </button>
        <button onClick={() => setMsg("")}>Clear message</button>
      </div>

      {msg && (
        <div style={{ marginBottom: 12, padding: 10, border: "1px solid #ddd" }}>
          {msg}
        </div>
      )}

      <h2 style={{ marginTop: 10 }}>New Acceptance</h2>
      <form onSubmit={submit} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <input
          placeholder="Company name"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          required
          style={{ minWidth: 260 }}
        />
        <input
          placeholder="Year"
          type="number"
          value={year}
          onChange={(e) => setYear(e.target.value)}
          required
          style={{ width: 120 }}
        />
        <input
          placeholder="Auditor"
          value={auditor}
          onChange={(e) => setAuditor(e.target.value)}
          style={{ width: 160 }}
        />
        <button type="submit">Save</button>
      </form>

      <h2 style={{ marginTop: 20 }}>Acceptance list</h2>

      {data.length === 0 ? (
        <div style={{ padding: 10, border: "1px solid #ddd" }}>
          No data yet.
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }} border="1" cellPadding="8">
            <thead>
              <tr>
                <th align="left">Company</th>
                <th align="left">Year</th>
                <th align="left">Auditor</th>
                <th align="left">Created</th>
                <th align="left">ID</th>
                <th align="left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <tr key={d._id}>
                  <td>{d.company_name}</td>
                  <td>{d.year}</td>
                  <td>{d.auditor}</td>
                  <td>{d.created_at || "-"}</td>
                  <td style={{ fontFamily: "monospace", fontSize: 12 }}>{d._id}</td>
                  <td style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button onClick={() => copyId(d._id)}>Copy ID</button>
                    <button onClick={() => remove(d._id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
