// src/routes/AppRoutes.tsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Signup from "@pages/SignUp/Signup";
import Login from "@pages/Login/Login";
import Dashboard from "@pages/dashboard/DashBoard";
import OAuthCallback from "@pages/OAuthCallback/OAuthCallback";
import { ProtectedRoute, PublicOnlyRoute } from "./guards/RouteGuards";
import Google2FASetup from "@pages/Google2FASetup/Google2FASetup";
import OAuthSuccessHandler from "@components/OAuthSuccessHandler/OAuthSuccessHandler";

export default function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/signup"
        element={
          <PublicOnlyRoute>
            <Signup />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <Login />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      <Route path="/oauth-callback" element={<OAuthCallback />} />
      <Route path="/google-2fa-setup" element={<Google2FASetup />} />
      <Route path="/login-success" element={<OAuthSuccessHandler />} />

      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}
