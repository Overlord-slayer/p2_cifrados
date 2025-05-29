import { useAuth } from "@store/useAuth";
import { JSX } from "react";
import { Navigate } from "react-router-dom";

export function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { accessToken } = useAuth();
  return accessToken ? children : <Navigate to="/login" />;
}

export function PublicOnlyRoute({ children }: { children: JSX.Element }) {
  const { accessToken } = useAuth();
  return accessToken ? <Navigate to="/chat" /> : children;
}
