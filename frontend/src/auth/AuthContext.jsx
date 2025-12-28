import { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });
  const [loading, setLoading] = useState(true);

  const setSession = (nextToken, nextUser) => {
    setToken(nextToken);
    setUser(nextUser);
    if (nextToken) localStorage.setItem("token", nextToken);
    else localStorage.removeItem("token");

    if (nextUser) localStorage.setItem("user", JSON.stringify(nextUser));
    else localStorage.removeItem("user");
  };

  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    const accessToken = res.data.access_token;
    const role = res.data.role;
    const name = res.data.name;

    // /auth/me дуудахгүйгээр шууд user object бүрдүүлж болно
    setSession(accessToken, { email, role, name });
    return { email, role, name };
  };

  const logout = () => {
    setSession("", null);
  };

  // refresh хийхэд token байвал /auth/me шалгана
  useEffect(() => {
    const run = async () => {
      try {
        if (!token) {
          setLoading(false);
          return;
        }
        const res = await api.get("/auth/me");
        setUser(res.data);
      } catch (e) {
        // token хүчингүй бол session цэвэрлэнэ
        setSession("", null);
      } finally {
        setLoading(false);
      }
    };
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthed: !!token,
      login,
      logout,
    }),
    [token, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
