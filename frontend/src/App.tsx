import React from "react";
import { BrowserRouter } from "react-router-dom";
import AppRoutes from "@routes/AppRoutes";
import { Header } from "@components/Header/Header";

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <AppRoutes />
    </BrowserRouter>
  );
}
