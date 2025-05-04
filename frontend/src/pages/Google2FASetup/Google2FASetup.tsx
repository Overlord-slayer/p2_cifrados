import React, { JSX, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import Toast from "@components/Toast/Toast";
import styles from "./Google2FASetup.module.css";

export default function Google2FASetup(): JSX.Element {
  const [email, setEmail] = useState("");
  const [totpSecret, setTotpSecret] = useState("");
  const [qrCode, setQrCode] = useState("");
  const [toastMessage, setToastMessage] = useState("");
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setEmail(params.get("email") || "");
    setTotpSecret(params.get("secret") || "");
    setQrCode(params.get("qr") || "");
  }, [location]);

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Configura tu autenticación de 2 pasos</h2>
        <p>Escanea este código QR en tu app de autenticación:</p>
        <img
          src={`data:image/png;base64,${qrCode}`}
          alt="QR Code para TOTP"
          className={styles.qr}
        />
        <p>O copia este código:</p>
        <code className={styles.code}>{totpSecret}</code>
        <p>Usa una app como Google Authenticator o Authy.</p>
      </div>

      {/* Mensaje emergente */}
      {toastMessage && <Toast message={toastMessage} type="success" />}
    </div>
  );
}
