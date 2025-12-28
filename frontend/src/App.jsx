import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import AuditorDashboard from "./pages/AuditorDashboard";
import AcceptanceDetail from "./pages/AcceptanceDetail";
import ProtectedRoute from "./auth/ProtectedRoute";
import { useAuth } from "./auth/AuthContext";

export default function App() {
  const { user, isAuthed, loading } = useAuth();

  if (loading) return <div className="p-6 text-slate-500">Loading...</div>;

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<Login />} />

      {/* Default redirect */}
      <Route
        path="/"
        element={
          isAuthed ? (
            <Navigate to={user?.role === "admin" ? "/admin" : "/auditor"} replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* Auditor */}
      <Route
        path="/auditor"
        element={
          <ProtectedRoute roles={["auditor", "admin"]}>
            <AuditorDashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/acceptance/:id"
        element={
          <ProtectedRoute roles={["auditor", "admin"]}>
            <AcceptanceDetail />
          </ProtectedRoute>
        }
      />

      {/* Admin route (түр placeholder) */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute roles={["admin"]}>
            <div className="p-6">Admin Dashboard (дараа нь хийе)</div>
          </ProtectedRoute>
        }
      />

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
