import React from "react";
import { BrowserRouter, useLocation } from "react-router-dom";
import AppRoutes from "@routes/AppRoutes";
import { Header } from "@components/Header/Header";

function AppContent() {
  const location = useLocation();

  // Ocultar Header si estás en la ruta /chat
  const hideHeader = location.pathname.startsWith("/chat");

  return (
    <div style={{height: "100%", width: "100%"}}>
      {!hideHeader && <Header />}
      <AppRoutes />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
