import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const nav = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("auditor@intax.mn");
  const [password, setPassword] = useState("auditor123");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const u = await login(email, password);
      // role-оор нь route хийх
      if (u.role === "admin") nav("/admin", { replace: true });
      else nav("/auditor", { replace: true });
    } catch (e2) {
      setErr("Нэвтрэх нэр/нууц үг буруу байна.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white border rounded-2xl p-6">
        <h1 className="text-2xl font-bold">INTAX Audit Portal</h1>
        <p className="text-sm text-slate-500 mt-1">
          Login (admin / auditor)
        </p>

        {err ? (
          <div className="mt-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {err}
          </div>
        ) : null}

        <form onSubmit={onSubmit} className="mt-5 space-y-3">
          <div>
            <div className="text-sm font-medium text-slate-700">Email</div>
            <input
              className="mt-1 w-full border rounded-xl px-3 py-2 outline-none focus:ring"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="auditor@intax.mn"
              autoComplete="email"
            />
          </div>

          <div>
            <div className="text-sm font-medium text-slate-700">Password</div>
            <input
              className="mt-1 w-full border rounded-xl px-3 py-2 outline-none focus:ring"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              type="password"
              autoComplete="current-password"
            />
          </div>

          <button
            disabled={loading}
            className="w-full mt-2 px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
}
