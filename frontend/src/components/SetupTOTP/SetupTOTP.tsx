import React, { JSX, useEffect, useState } from "react";
import { useAuth } from "@store/useAuth";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import styles from "./SetupTOTP.module.css";
import Toast from "@components/Toast/Toast";

interface TOTPSetupResponse {
  totp_secret: string;
  qr_code_base64: string;
}

/**
 * Componente SetupTOTP
 * 
 * Se muestra después de que el usuario se registra y hace login por primera vez.
 * Permite configurar la autenticación de dos factores (2FA) usando TOTP.
 */
export default function SetupTOTP(): JSX.Element {
  const [qrCode, setQrCode] = useState<string>("");
  const [totpSecret, setTotpSecret] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<"success" | "error">("success");

  const { accessToken } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }

    fetchTOTPSetup();
  }, [accessToken, navigate]);

  const fetchTOTPSetup = async () => {
    try {
      setLoading(true);
      const response = await axios.get<TOTPSetupResponse>(
        "/auth/totp-setup",
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      setQrCode(response.data.qr_code_base64);
      setTotpSecret(response.data.totp_secret);
      setError("");
    } catch (err: any) {
      console.error("Error fetching TOTP setup:", err);
      setError("Error al cargar la configuración de autenticación.");
      
      if (err.response?.status === 401) {
        setToastMessage("Sesión expirada. Por favor, inicia sesión nuevamente.");
        setToastType("error");
        setTimeout(() => navigate("/login"), 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteSetup = () => {
    setToastMessage("Configuración completada. Ya puedes usar la aplicación.");
    setToastType("success");
    
    setTimeout(() => {
      navigate("/chat");
    }, 1500);
  };

  const handleSkipForNow = () => {
    // Nota: En un entorno real, es posible que no quieras permitir omitir la configuración 2FA
    setToastMessage("Configuración omitida. Recuerda configurar 2FA más tarde para mayor seguridad.");
    setToastType("error");
    
    setTimeout(() => {
      navigate("/chat");
    }, 2000);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setToastMessage("Código copiado al portapapeles");
      setToastType("success");
    } catch (err) {
      console.error("Error copying to clipboard:", err);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.card}>
          <div className={styles.loading}>
            <p>Cargando configuración de autenticación...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.card}>
          <div className={styles.error}>
            <h2>Error</h2>
            <p>{error}</p>
            <button 
              onClick={() => navigate("/login")} 
              className={styles.button}
            >
              Volver al login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Configurar Autenticación de Dos Factores</h2>
        
        <div className={styles.content}>
          <div className={styles.instructions}>
            <p>Para completar tu registro, necesitas configurar la autenticación de dos factores (2FA):</p>
            <ol>
              <li>Instala una aplicación de autenticación como <strong>Google Authenticator</strong> o <strong>Authy</strong></li>
              <li>Escanea el código QR que aparece abajo</li>
              <li>Si no puedes escanear el QR, copia y pega el código manualmente</li>
              <li>¡Listo! Ya podrás iniciar sesión usando tu código TOTP</li>
            </ol>
          </div>

          <div className={styles.qrSection}>
            <h3>Código QR</h3>
            {qrCode && (
              <img
                src={`data:image/png;base64,${qrCode}`}
                alt="TOTP QR Code"
                className={styles.qrCode}
              />
            )}
          </div>

          <div className={styles.secretSection}>
            <h3>Código Manual</h3>
            <p>Si no puedes escanear el QR, usa este código:</p>
            <div className={styles.secretContainer}>
              <code className={styles.secret}>{totpSecret}</code>
              <button 
                onClick={() => copyToClipboard(totpSecret)}
                className={styles.copyButton}
              >
                Copiar
              </button>
            </div>
          </div>

          <div className={styles.actions}>
            <button 
              onClick={handleCompleteSetup}
              className={styles.primaryButton}
            >
              Configuración Completada
            </button>
            <button 
              onClick={handleSkipForNow}
              className={styles.secondaryButton}
            >
              Saltar por ahora
            </button>
          </div>
        </div>
      </div>

      {toastMessage && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setToastMessage("")}
        />
      )}
    </div>
  );
}
