import React, { JSX, useEffect, useState } from "react";
import { signin } from "@api/api";
import { useAuth } from "@store/useAuth";
import { validateEmail } from "@constants/validatros";
import { useNavigate } from "react-router-dom";
import Toast from "@components/Toast/Toast";
import styles from "./Login.module.css";
import { googleLoginUrl } from "@api/api";
import { loadUsername } from "@store/userStore";
import { devLog, devError } from "@api/logger";

/**
 * Componente `Login`.
 *
 * Representa la vista de inicio de sesión del sistema, donde el usuario debe ingresar:
 * - correo electrónico,
 * - contraseña,
 * - y código TOTP (de autenticación en dos pasos).
 *
 * Este componente incluye validaciones en el frontend, autenticación asíncrona con el backend, y gestión de tokens de sesión.
 *
 * Si el usuario ya está autenticado (tiene `accessToken`), se redirige automáticamente al dashboard.
 *
 * @component
 * @returns {JSX.Element} Interfaz de login con campos de entrada y mensajes de error/toast.
 *
 * @example
 * ```tsx
 * <Login />
 * ```
 */
export default function Login(): JSX.Element {
	// Estados locales para capturar las entradas del usuario
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [totp, setTotp] = useState("");

	// Estados para mostrar mensajes emergentes (toast)
	const [toastMessage, setToastMessage] = useState("");
	const [toastType, setToastType] = useState<"success" | "error">("success");

	const { setTokens, accessToken } = useAuth();
	const navigate = useNavigate();

	/**
	 * Redirige automáticamente al dashboard si el usuario ya tiene un token válido.
	 */
	useEffect(() => {
		if (accessToken) {
			loadUsername(accessToken)
			navigate("/chat");
		}
	}, [accessToken, navigate]);

	/**
	 * Maneja el proceso de inicio de sesión.
	 *
	 * Realiza las siguientes acciones:
	 * - Valida campos de entrada localmente.
	 * - Llama al endpoint `signin` para autenticación.
	 * - Almacena los tokens (access y refresh) usando el contexto `useAuth`.
	 * - Muestra mensajes de error o éxito mediante `Toast`.
	 */
	const handleLogin = async () => {
		// Log seguro: password y totp serán redactados automáticamente
		devLog("Iniciando login para:", { email });

		// Validaciones básicas de campos
		if (!email || !password || !totp) {
			setToastMessage("Todos los campos son obligatorios.");
			setToastType("error");
			return;
		}
		if (!validateEmail(email)) {
			setToastMessage("Correo inválido.");
			setToastType("error");
			return;
		}
		if (password.length < 8) {
			setToastMessage("La contraseña debe tener al menos 8 caracteres.");
			setToastType("error");
			return;
		}
		if (totp.length !== 6 || !/^\d{6}$/.test(totp)) {
			setToastMessage("El código TOTP debe tener 6 dígitos numéricos.");
			setToastType("error");
			return;
		}

		// Llamada a la API y manejo de tokens
		try {
			const res = await signin(email, password, totp);
			const { access_token, refresh_token } = res.data;

			devLog("Login exitoso para:", { email });
			
			// Guardar tokens primero
			localStorage.setItem("access_token", access_token);
			localStorage.setItem("refresh_token", refresh_token);
			setTokens(access_token, refresh_token);

			// Cargar username antes de navegar
			await loadUsername(access_token);

			setToastMessage("Inicio de sesión exitoso.");
			setToastType("success");

			// Navegar después de un breve delay
			setTimeout(() => {
				setToastMessage("");
				navigate("/chat");
			}, 500);
		} catch (e) {
			devError("Error en login:", e);
			setToastMessage(`Error al iniciar sesión. Revisa tus datos.`);
			setToastType("error");
		}
	};

	return (
		<div className={styles.container}>
			<div className={styles.card}>
				<h2 className={styles.title}>Login</h2>

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
					<input
						placeholder="Código TOTP"
						onChange={(e) => setTotp(e.target.value)}
						className={styles.input}
					/>
					<button onClick={handleLogin} className={styles.button}>
						Iniciar sesión
					</button>
					<button
						onClick={() => (window.location.href = googleLoginUrl)}
						className={styles.googleButton}
					>
						Iniciar sesión con Google
					</button>
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
