import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
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
