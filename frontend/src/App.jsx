import { Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import AuditorDashboard from "./pages/AuditorDashboard";
import AcceptanceDetail from "./pages/AcceptanceDetail";

import ProtectedRoute from "./auth/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      {/* Default */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Public */}
      <Route path="/login" element={<Login />} />

      {/* Auditor Dashboard */}
      <Route
        path="/auditor"
        element={
          <ProtectedRoute allowedRoles={["auditor", "admin"]}>
            <AuditorDashboard />
          </ProtectedRoute>
        }
      />

      {/* Acceptance Detail */}
      <Route
        path="/acceptance/:id"
        element={
          <ProtectedRoute allowedRoles={["auditor", "admin"]}>
            <AcceptanceDetail />
          </ProtectedRoute>
        }
      />

      {/* 404 */}
      <Route path="*" element={<div className="p-6">404 Not Found</div>} />
    </Routes>
  );
}
