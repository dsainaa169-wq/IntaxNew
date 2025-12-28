import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function ProtectedRoute({ children, roles }) {
  const { isAuthed, user, loading } = useAuth();

  if (loading) return <div className="p-6 text-slate-500">Loading...</div>;

  if (!isAuthed) return <Navigate to="/login" replace />;

  if (roles?.length && user?.role && !roles.includes(user.role)) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
