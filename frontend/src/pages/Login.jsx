import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");

    try {
      const u = await login({ email, password });
      // auditor/admin аль аль нь auditor dashboard руу түр орно
      nav("/auditor");
    } catch (e2) {
      setErr("Нэвтрэхэд алдаа гарлаа.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="w-full max-w-md bg-white rounded-2xl shadow p-6">
        <h1 className="text-2xl font-bold text-slate-900">INTAX Audit Portal</h1>
        <p className="text-slate-500 mt-1">Login</p>

        {err ? (
          <div className="mt-3 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {err}
          </div>
        ) : null}

        <form onSubmit={onSubmit} className="mt-5 space-y-3">
          <div>
            <label className="text-sm text-slate-600">Email</label>
            <input
              className="mt-1 w-full border rounded-xl px-3 py-2 outline-none focus:ring"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="auditor@intax.mn"
            />
          </div>

          <div>
            <label className="text-sm text-slate-600">Password</label>
            <input
              className="mt-1 w-full border rounded-xl px-3 py-2 outline-none focus:ring"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              placeholder="••••••••"
            />
          </div>

          <button className="w-full rounded-xl bg-blue-600 text-white py-2 font-semibold hover:bg-blue-700">
            Нэвтрэх
          </button>

          <div className="text-xs text-slate-500">
            <span className="font-medium">Туршилт:</span> admin гэж email-дээ
            оруулбал role=admin болно.
          </div>
        </form>
      </div>
    </div>
  );
}
