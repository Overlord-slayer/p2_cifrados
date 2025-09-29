import React, { JSX, useState, useEffect } from "react";
import { signup } from "@api/api";
import { validateEmail } from "@constants/validatros";
import { useNavigate, useLocation } from "react-router-dom";
import styles from "./Signup.module.css";
import Toast from "@components/Toast/Toast";
import { AxiosError } from "axios";

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
  const location = useLocation(); // Para acceder a los parámetros de la URL

  // Verificar si el parámetro google_authenticated está presente en la URL
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    if (queryParams.has("google_authenticated")) {
      setToastMessage("Este correo ya está autenticado con Google.");
      setToastType("error");
    }
  }, [location]);

  /**
   * Maneja el flujo de registro del usuario.
   */

  const handleSignup = async () => {
    console.log("Datos que se envían al backend:", { email, password });

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
    } catch (e: unknown) {
      // Usar `unknown` en lugar de `AxiosError`
      console.error("Error durante el registro:", e);

      // Asegurarse de que `e` es un AxiosError
      if (e instanceof AxiosError) {
        // Verificar si es una instancia de AxiosError
        // Verificar si el error es por un correo ya registrado
        if (e?.response?.data?.detail === "Email already registered") {
          setToastMessage(
            "Este correo electrónico ya está registrado. ¿Quieres iniciar sesión?"
          );
          setToastType("error");
        } else {
          setToastMessage("Error durante el registro. Inténtalo de nuevo.");
          setToastType("error");
        }
      } else {
        // Si el error no es un AxiosError, manejamos el error genérico
        setToastMessage("Error desconocido. Inténtalo de nuevo.");
        setToastType("error");
      }
    }
  };

  // Redirigir al usuario al flujo de Google OAuth
  const handleGoogleSignup = () => {
    window.location.href = "http://localhost:8000/auth/google/login";
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

            {/* Botón para registrar con Google */}
            <button
              onClick={handleGoogleSignup}
              className={`${styles.button} ${styles.googleButton}`}
            >
              Registrarse con Google
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
