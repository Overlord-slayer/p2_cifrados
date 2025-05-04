import { useLocation, useNavigate } from "react-router-dom";
import styles from "./SetupTOTP.module.css";

/**
 * Componente que muestra el QR y código secreto tras login con Google.
 */
export default function SetupTOTP() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.email || !state?.qr || !state?.secret) {
    return <p>Información incompleta. Vuelve a intentar.</p>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Configura tu autenticador</h2>
        <p>Escanea este código QR en tu app de autenticación:</p>
        <img
          src={`data:image/png;base64,${state.qr}`}
          alt="TOTP QR Code"
          className={styles.qr}
        />
        <p>
          O copia este código manualmente:
          <code className={styles.code}>{state.secret}</code>
        </p>
        <button onClick={() => navigate("/login")} className={styles.button}>
          Ir al login
        </button>
      </div>
    </div>
  );
}
