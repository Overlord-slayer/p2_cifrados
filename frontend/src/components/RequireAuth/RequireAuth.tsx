import React, { JSX, useEffect } from "react";
import { useAuth } from "@store/useAuth";
import { useNavigate } from "react-router-dom";

/**
 * Componente `RequireAuth`.
 *
 * Este componente actúa como un **wrapper (envoltorio) de protección de rutas**, permitiendo renderizar contenido hijo
 * **solo si el usuario está autenticado** (es decir, si tiene un `accessToken` válido).
 *
 * Comportamiento:
 * - Obtiene el token de acceso (`accessToken`) desde el hook de autenticación personalizado `useAuth`.
 * - Si no hay un token válido, redirige automáticamente al usuario a la ruta `/login`.
 * - Si el token es válido, renderiza el contenido hijo (`children`) normalmente.
 *
 * Este componente es útil cuando necesitas protección adicional **dentro de otros componentes**, sin depender
 * del enrutador de React (`Route`) o lógica en `App.tsx`.
 *
 * @component
 * @param {object} props - Props del componente.
 * @param {React.ReactNode} props.children - Elementos React hijos que se renderizarán si hay autenticación.
 * @returns {JSX.Element} Elemento React protegido por validación de token.
 *
 * @example
 * ```tsx
 * <RequireAuth>
 *   <ContenidoPrivado />
 * </RequireAuth>
 * ```
 */
export const RequireAuth = ({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element => {
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  /**
   * Efecto que se ejecuta al montar el componente o cuando cambia el token.
   *
   * Si no hay token (`accessToken`), redirige al usuario a `/login`.
   */
  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
    }
  }, [accessToken, navigate]);

  // Solo renderiza los hijos si hay un token válido
  return <>{accessToken && children}</>;
};
