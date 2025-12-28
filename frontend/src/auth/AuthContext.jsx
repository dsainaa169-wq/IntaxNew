import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  const login = async ({ email, password }) => {
    // ✅ ОДОО: хамгийн энгийн mock login.
    // Дараа нь backend /auth/login болгоод token + role авч set хийнэ.
    const role = email?.toLowerCase().includes("admin") ? "admin" : "auditor";

    const fakeToken = "dev-token";
    localStorage.setItem("token", fakeToken);

    const u = { email, role };
    localStorage.setItem("user", JSON.stringify(u));
    setUser(u);

    return u;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  const value = useMemo(() => ({ user, login, logout }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
