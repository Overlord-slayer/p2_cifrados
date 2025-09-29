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
  const [registered, setRegistered] = useState<boolean>(false);
  const [registrationMessage, setRegistrationMessage] = useState<string>("");

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
      setToastMessage("La contraseña debe tener al menos 8 caracteres y contener: mayúscula, minúscula, número y carácter especial.");
      setToastType("error");
      return;
    }

    // Validaciones de contraseña más estrictas según el backend
    if (!/[A-Z]/.test(password)) {
      setToastMessage("La contraseña debe contener al menos una letra mayúscula.");
      setToastType("error");
      return;
    }
    if (!/[a-z]/.test(password)) {
      setToastMessage("La contraseña debe contener al menos una letra minúscula.");
      setToastType("error");
      return;
    }
    if (!/\d/.test(password)) {
      setToastMessage("La contraseña debe contener al menos un número.");
      setToastType("error");
      return;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      setToastMessage("La contraseña debe contener al menos un carácter especial.");
      setToastType("error");
      return;
    }

    // Llamada a la API
    try {
      const res = await signup(email, password);
      console.log("Signup OK:", res.data);
      
      // El backend ahora devuelve: { email, message, setup_required }
      setRegistrationMessage(res.data.message || "Cuenta creada exitosamente");
      setRegistered(true);
      setToastMessage("Registro exitoso. Ahora debes iniciar sesión para configurar la autenticación de dos factores.");
      setToastType("success");
    } catch (e: unknown) {
      console.error("Error durante el registro:", e);

      if (e instanceof AxiosError) {
        // El backend ahora devuelve mensajes más genéricos por seguridad
        const errorMessage = e?.response?.data?.detail || "Error durante el registro";
        
        if (errorMessage === "Invalid request data") {
          setToastMessage("Los datos proporcionados no son válidos. Verifica tu contraseña.");
          setToastType("error");
        } else {
          setToastMessage(errorMessage);
          setToastType("error");
        }
      } else {
        setToastMessage("Error de conexión. Inténtalo de nuevo.");
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
          // Vista después de registrarse: explicación del nuevo flujo
          <div className={styles.result}>
            <p className={styles.success}>¡Registro exitoso!</p>
            <p>{registrationMessage}</p>
            <div className={styles.instructions}>
              <p><strong>Pasos siguientes:</strong></p>
              <ol>
                <li>Haz clic en "Ir al login" para iniciar sesión</li>
                <li>Después del login, accederás automáticamente a la configuración de autenticación de dos factores (2FA)</li>
                <li>Escanea el código QR con tu aplicación de autenticación (Google Authenticator, Authy, etc.)</li>
                <li>¡Listo! Tu cuenta estará completamente configurada</li>
              </ol>
            </div>
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
