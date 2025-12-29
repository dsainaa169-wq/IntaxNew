import axios from "axios";

const API = import.meta.env.VITE_API_URL;

export async function login(email, password) {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const res = await axios.post(`${API}/auth/login`, body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  localStorage.setItem("access_token", res.data.access_token);
  return res.data;
}
