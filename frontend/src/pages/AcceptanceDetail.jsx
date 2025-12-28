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
        // ✅ Backend дээр GET /acceptance (list) л байгаа учраас
        // list татаж аваад id-гаар нь олж харуулна.
        const res = await api.get("/acceptance");
        const list = Array.isArray(res.data) ? res.data : [];

        const found = list.find((x) => {
          const itemId = x.id ?? x._id ?? x.clientId;
          return String(itemId) === String(id);
        });

        if (!found) {
          setData(null);
          setErr("Энэ ID-тай acceptance олдсонгүй.");
          return;
        }

        setData(found);
      } catch (e) {
        setErr(
          "Acceptance detail татаж чадсангүй. GET /acceptance ажиллаж байгаа эсэхээ шалга."
        );
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
              {data.companyName || data.clientType || "Acceptance Detail"}
            </h1>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <Field label="Client Type" value={data.clientType} />
              <Field label="Company Name" value={data.companyName} />
              <Field label="Revenue" value={data.revenue} />
              <Field label="Total Assets" value={data.totalAssets} />
              <Field label="Created At" value={data.createdAt} />
              <Field label="ID" value={data.id || data._id} />
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
