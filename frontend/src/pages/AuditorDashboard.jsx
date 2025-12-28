import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";

export default function AuditorDashboard() {
  const { user, logout } = useAuth();
  const nav = useNavigate();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const load = async () => {
    setLoading(true);
    setErr("");
    try {
      const res = await api.get("/acceptance");
      setItems(Array.isArray(res.data) ? res.data : []);
    } catch (e) {
      setErr("Acceptance list татаж чадсангүй. Token/Backend/CORS шалга.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onLogout = () => {
    logout();
    nav("/login");
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Auditor Dashboard</h1>
            <div className="text-sm text-slate-500">
              {user?.email || "user"} • role: {user?.role || "auditor"}
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={load}
              className="px-4 py-2 rounded-xl border bg-white hover:bg-slate-50"
            >
              Refresh
            </button>
            <button
              onClick={onLogout}
              className="px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-6">
        {err ? (
          <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {err}
          </div>
        ) : null}

        {loading ? (
          <div className="text-slate-500">Loading...</div>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Acceptance List</h2>
              <div className="text-sm text-slate-500">Нийт: {items.length}</div>
            </div>

            <div className="mt-4 grid gap-3">
              {items.map((a) => {
                const id = a.id ?? a._id ?? a.acceptance_id;
                return (
                  <Link
                    key={String(id)}
                    to={`/acceptance/${id}`}
                    className="block bg-white border rounded-2xl p-4 hover:shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-semibold text-slate-900">
                          {a.company_name || a.companyName || "Unnamed company"}
                        </div>
                        <div className="mt-1 text-sm text-slate-600">
                          auditor: {a.auditor || "-"} • year: {a.year ?? "-"}
                        </div>
                      </div>
                      <div className="text-xs text-slate-500">{String(id)}</div>
                    </div>
                  </Link>
                );
              })}

              {!items.length ? (
                <div className="text-slate-500 mt-6">Одоогоор data алга.</div>
              ) : null}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
