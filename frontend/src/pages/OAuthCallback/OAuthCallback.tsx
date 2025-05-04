import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@store/useAuth";

export default function OAuthCallback() {
  const navigate = useNavigate();
  const { setTokens } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    if (accessToken && refreshToken) {
      setTokens(accessToken, refreshToken);
      navigate("/dashboard");
    } else {
      navigate("/login"); // Redirige si faltan tokens
    }
  }, [navigate, setTokens]);

  return <p>Procesando autenticación de Google...</p>;
}
