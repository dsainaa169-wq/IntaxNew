import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api/client";

export default function AcceptanceDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setErr("");
      try {
        const res = await api.get(`/acceptance/${id}`);
        setData(res.data);
      } catch (e) {
        setErr("Acceptance detail татаж чадсангүй. Token/Endpoint шалга.");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [id]);

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <Link to="/auditor" className="text-blue-600 hover:underline">
            ← Back to Dashboard
          </Link>
          <div className="text-xs text-slate-500">ID: {id}</div>
        </div>

        {loading ? <div className="mt-6 text-slate-500">Loading...</div> : null}

        {err ? (
          <div className="mt-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {err}
          </div>
        ) : null}

        {data ? (
          <div className="mt-4 bg-white border rounded-2xl p-5">
            <h1 className="text-xl font-bold">
              {data.company_name || data.companyName || "Acceptance Detail"}
            </h1>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <Field label="Year" value={data.year} />
              <Field label="Auditor" value={data.auditor} />
              <Field label="Status" value={data.status} />
              <Field label="Created By" value={data.created_by} />
            </div>

            <div className="mt-4">
              <div className="text-sm font-semibold text-slate-700">Raw JSON</div>
              <pre className="mt-2 text-xs bg-slate-50 border rounded-xl p-3 overflow-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Field({ label, value }) {
  return (
    <div className="border rounded-xl p-3 bg-slate-50">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 font-medium text-slate-900">{value ?? "-"}</div>
    </div>
  );
}
