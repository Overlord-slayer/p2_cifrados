// src/routes/AppRoutes.tsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Signup from "@pages/SignUp/Signup";
import Login from "@pages/Login/Login";
import Dashboard from "@pages/dashboard/DashBoard";
import { ProtectedRoute, PublicOnlyRoute } from "./guards/RouteGuards";

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
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}
