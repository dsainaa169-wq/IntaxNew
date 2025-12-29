// src/auth/AuthContext.jsx
import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { api, API_URL } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);      // {email, role, name}
  const [loading, setLoading] = useState(true);

  // App эхлэхэд token байвал /auth/me дуудаж user-г сэргээх
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }

    api.get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("access_token");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  // ✅ LOGIN — хамгийн чухал хэсэг:
  // Backend чинь OAuth2PasswordRequestForm болсон тул JSON биш
  // application/x-www-form-urlencoded байдлаар username/password явуулна.
  const login = async (email, password) => {
    const body = new URLSearchParams();
    body.append("username", (email || "").trim()); // form.username
    body.append("password", password || "");

    const res = await axios.post(`${API_URL}/auth/login`, body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    // res.data = { access_token, token_type, role, name }
    localStorage.setItem("access_token", res.data.access_token);

    // Token хадгалсны дараа /auth/me дуудаж user мэдээллээ авна
    const me = await api.get("/auth/me");
    setUser(me.data);

    // Login.jsx чинь u.role ашиглаж route хийдэг тул role/name-г буцаана
    return { ...me.data, role: me.data.role, name: me.data.name };
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, loading, login, logout, isAuthed: !!user }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth() must be used inside <AuthProvider>");
  return ctx;
}
