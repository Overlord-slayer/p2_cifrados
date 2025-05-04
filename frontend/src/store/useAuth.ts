import { create } from "zustand";

/**
 * Interfaz que define el estado de autenticación.
 *
 * @property {string | null} accessToken - Token JWT de acceso del usuario.
 * @property {string | null} refreshToken - Token para renovar el JWT de acceso.
 * @property {(access: string, refresh: string) => void} setTokens - Función para guardar y actualizar ambos tokens.
 * @property {() => void} logout - Función para eliminar los tokens y cerrar sesión.
 */
interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  logout: () => void;
}

/**
 * Hook personalizado `useAuth` basado en Zustand.
 *
 * Este hook proporciona un estado global de autenticación que se mantiene sincronizado con `localStorage`.
 * Es utilizado por componentes como `Login`, `ProtectedRoute` y `Dashboard` para verificar si el usuario está autenticado
 * y para manejar el inicio/cierre de sesión.
 *
 * Comportamiento:
 * - Al inicializarse, recupera `accessToken` y `refreshToken` desde `localStorage`.
 * - Permite guardar nuevos tokens con `setTokens`.
 * - Permite cerrar sesión eliminando los tokens del estado y del almacenamiento local.
 *
 * @returns {AuthState} Estado y acciones relacionadas con autenticación.
 *
 * @example
 * ```tsx
 * const { accessToken, setTokens, logout } = useAuth();
 * ```
 */
export const useAuth = create<AuthState>((set) => ({
  // Inicialización: recupera los tokens guardados (si existen)
  accessToken: localStorage.getItem("accessToken"),
  refreshToken: localStorage.getItem("refreshToken"),

  /**
   * Guarda los tokens en localStorage y actualiza el estado global.
   * @param accessToken - JWT de acceso
   * @param refreshToken - Token de actualización
   */
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
    set({ accessToken, refreshToken });
  },

  /**
   * Elimina los tokens del estado y del localStorage (cierre de sesión).
   */
  logout: () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    set({ accessToken: null, refreshToken: null });
  },
}));
