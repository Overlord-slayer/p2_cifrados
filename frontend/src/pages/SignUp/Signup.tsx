import React, { JSX, useState } from "react";
import { signup } from "@api/api";
import { validateEmail } from "@constants/validatros";
import { useNavigate } from "react-router-dom";
import styles from "./Signup.module.css";
import Toast from "@components/Toast/Toast";

/**
 * Componente `Signup`.
 *
 * Este componente gestiona el registro de nuevos usuarios. Permite al usuario ingresar su correo electrónico
 * y contraseña, y tras registrarse exitosamente, le muestra un código QR para configurar la autenticación en dos pasos (TOTP).
 *
 * Características:
 * - Validaciones de entrada para correo y contraseña.
 * - Llamada al backend para registrar el usuario.
 * - Muestra código QR y clave secreta TOTP para apps como Google Authenticator.
 * - Muestra mensajes emergentes (`Toast`) para éxito o error.
 *
 * @component
 * @returns {JSX.Element} Vista de formulario de registro o código TOTP tras registro exitoso.
 *
 * @example
 * ```tsx
 * <Signup />
 * ```
 */
export default function Signup(): JSX.Element {
  // Estados para los campos de entrada
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  // Estados para datos devueltos tras el registro
  const [qrCode, setQrCode] = useState<string>("");
  const [totpSecret, setTotpSecret] = useState<string>("");
  const [registered, setRegistered] = useState<boolean>(false);

  // Estados para mensajes emergentes
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<"success" | "error">("success");

  const navigate = useNavigate();

  /**
   * Maneja el flujo de registro del usuario.
   *
   * Realiza las siguientes acciones:
   * - Verifica que los campos estén completos y válidos.
   * - Llama a la API `signup` para registrar al usuario.
   * - Si tiene éxito, muestra un código QR y una clave TOTP.
   * - Si falla, muestra un mensaje de error mediante `Toast`.
   */
  const handleSignup = async () => {
    console.log("Intentando registrar usuario:", { email, password });

    // Validaciones básicas
    if (!email || !password) {
      setToastMessage("Todos los campos son obligatorios.");
      setToastType("error");
      return;
    }
    if (!validateEmail(email)) {
      setToastMessage("El correo electrónico no es válido.");
      setToastType("error");
      return;
    }
    if (password.length < 8) {
      setToastMessage("La contraseña debe tener al menos 8 caracteres.");
      setToastType("error");
      return;
    }

    // Llamada a la API
    try {
      const res = await signup(email, password);
      console.log("Signup OK:", res.data);

      setQrCode(res.data.qr_code_base64);
      setTotpSecret(res.data.totp_secret);
      setRegistered(true);
      setToastMessage("Registro exitoso.");
      setToastType("success");
    } catch (e) {
      console.error("Error durante el registro:", e);
      setToastMessage("Error durante el registro. Inténtalo de nuevo.");
      setToastType("error");
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Registro</h2>

        {/* Formulario antes de registrarse */}
        {!registered ? (
          <div className={styles.form}>
            <input
              placeholder="Correo electrónico"
              onChange={(e) => setEmail(e.target.value)}
              className={styles.input}
            />
            <input
              placeholder="Contraseña"
              type="password"
              onChange={(e) => setPassword(e.target.value)}
              className={styles.input}
            />
            <button onClick={handleSignup} className={styles.button}>
              Crear cuenta
            </button>
          </div>
        ) : (
          // Vista después de registrarse: muestra QR y secreto TOTP
          <div className={styles.result}>
            <p className={styles.success}>Registro exitoso</p>
            <p>Escanea este código QR en tu app de autenticación:</p>
            <img
              src={`data:image/png;base64,${qrCode}`}
              alt="TOTP QR Code"
              className={styles.qr}
            />
            <p>
              O copia este código:
              <code className={styles.code}>{totpSecret}</code>
            </p>
            <button
              onClick={() => navigate("/login")}
              className={styles.buttonAlt}
            >
              Ir al login
            </button>
          </div>
        )}
      </div>

      {/* Mensaje emergente */}
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
