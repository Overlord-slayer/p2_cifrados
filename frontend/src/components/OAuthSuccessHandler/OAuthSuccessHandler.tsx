import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useAuth } from "@store/useAuth";
import styles from "./OAuthSuccessHandler.module.css";

/**
 * Componente que maneja la respuesta de Google OAuth.
 * - Si el usuario es nuevo, lo redirige a configurar TOTP.
 * - Si el usuario ya existe, guarda los tokens y redirige al dashboard.
 */
export default function OAuthSuccessHandler() {
  const [params] = useSearchParams();
  const { setTokens } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");
    const email = params.get("email");
    const secret = params.get("secret");
    const qr = params.get("qr");

    if (email && secret && qr) {
      // Nuevo usuario de Google → configurar TOTP
      navigate("/setup-totp", {
        state: { email, secret, qr },
      });
      return;
    }

    if (accessToken && refreshToken) {
      setTokens(accessToken, refreshToken);
      navigate("/dashboard");
    } else {
      navigate("/login");
    }
  }, [params, navigate, setTokens]);

  return (
    <div className={styles.container}>
      <p className={styles.message}>Procesando autenticación...</p>
    </div>
  );
}
