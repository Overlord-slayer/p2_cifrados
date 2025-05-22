import React, { JSX, useEffect } from "react";
import { useAuth } from "@store/useAuth";
import { useNavigate } from "react-router-dom";
import { RequireAuth } from "@components/RequireAuth/RequireAuth";
import styles from "./DashBoard.module.css";
import ChatPage from "@pages/chat/ChatPage";

/**
 * Componente `Dashboard`.
 *
 * Representa una página protegida que solo puede ser accedida por usuarios autenticados.
 *
 * Este componente realiza lo siguiente:
 * - Verifica si el usuario tiene un token de acceso (`accessToken`) usando el hook `useAuth`.
 * - Si el usuario no está autenticado, redirige automáticamente a la ruta `/login` usando `useNavigate` de React Router.
 * - Si el usuario está autenticado, muestra un mensaje de bienvenida dentro de un contenedor protegido por `RequireAuth`.
 *
 * El contenido está estilizado mediante un módulo CSS (`Dashboard.module.css`).
 *
 * @componente
 * @ejemplo
 * ```tsx
 * <Dashboard />
 * ```
 * @returns JSX.Element Página de dashboard protegida con mensaje de bienvenida.
 */
export default function Dashboard(): JSX.Element {
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  /**
   * Efecto que se ejecuta al montar el componente y cuando cambia `accessToken`.
   *
   * Si el token de acceso no está presente, se redirige al usuario a la pantalla de login.
   */
  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
    }
  }, [accessToken, navigate]);

  return (
    <RequireAuth>
      {/* <div className={styles.container}>Bienvenido al Dashboard seguro</div> */}
      <ChatPage />
    </RequireAuth>
  );
}
