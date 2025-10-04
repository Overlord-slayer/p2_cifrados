import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

// Interceptor: añade automáticamente el token a todas las peticiones
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de respuesta: manejar token expirado
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido - limpiar y redirigir
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      // El componente RequireAuth manejará la redirección
    }
    return Promise.reject(error);
  }
);

export const signup = (email: string, password: string) =>
  API.post(
    "/auth/signup",
    { email, password },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

export const signin = (email: string, password: string, totp_code: string) =>
  API.post("/auth/login", { email, password, totp_code });

export const googleLoginUrl = "http://localhost:8000/auth/google/login";
export default API;
