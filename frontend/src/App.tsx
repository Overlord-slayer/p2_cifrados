import React from "react";
import { BrowserRouter, useLocation } from "react-router-dom";
import AppRoutes from "@routes/AppRoutes";
import { Header } from "@components/Header/Header";

function AppContent() {
  const location = useLocation();

  // Ocultar Header si estás en la ruta /chat
  const hideHeader = location.pathname.startsWith("/chat");

  return (
    <>
      {!hideHeader && <Header />}
      <AppRoutes />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
