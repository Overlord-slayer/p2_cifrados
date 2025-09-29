import axios from "axios";

// Use relative URLs so Vite proxy can handle them (avoids CORS issues in development)
const API = axios.create({
  baseURL: "",
});

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

export const googleLoginUrl = "/auth/google/login";
export default API
