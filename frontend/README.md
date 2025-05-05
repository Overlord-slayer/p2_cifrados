# Frontend de Autenticación Segura (React + TypeScript)

Este proyecto representa el frontend de una aplicación web con autenticación segura. Incluye soporte para inicio de sesión local, autenticación con Google (OAuth 2.0), TOTP como segundo factor, y protección de rutas privadas mediante tokens JWT.

---

## Estructura del Proyecto

```
src/
├── assets/               # Archivos estáticos
├── components/           # Componentes reutilizables
│   ├── Header/           # Encabezado principal
│   ├── RequireAuth.tsx   # Protección de rutas privadas
│   ├── SetupTOTP/        # Configuración de TOTP
│   └── Toast/            # Notificaciones
├── constants/            # Constantes globales
├── lib/                  # Cliente API (axios/fetch)
├── pages/                # Páginas del sistema
│   ├── dashboard/        # Ruta protegida principal
│   ├── login/            # Inicio de sesión local
│   ├── OAuthCallback/    # Redirección OAuth2 de Google
│   ├── setupTOTP/        # Configuración de TOTP
│   └── signup/           # Registro de usuario
├── routes/               # Ruteo con protección
├── store/                # Estado global (Zustand)
├── App.tsx               # Componente principal
└── index.css             # Estilos globales
```

---

## Autenticación

### Inicio de sesión local:

1. El usuario ingresa email y contraseña.
2. Si tiene TOTP activado, se le redirige a `/setup-totp` para verificación.
3. Si no, el token es almacenado en el estado global y se accede al dashboard.

### Google OAuth2:

1. Se inicia el flujo de autenticación con Google.
2. Tras la redirección a `/oauth/callback`, el token es procesado y almacenado.
3. Si el usuario es nuevo, se le pide configurar TOTP si es requerido. (Esto falto)

---

## Protección de Rutas: `RequireAuth.tsx`

Este componente actúa como guard para rutas privadas:

```tsx
<RequireAuth>
  <Dashboard />
</RequireAuth>
```

- Usa `useAuth()` desde Zustand para verificar si hay `accessToken`.
- Si no existe, redirige a `/login`.
- Solo renderiza los hijos si el token es válido.

---

## Manejo de Estado Global con Zustand

Este proyecto utiliza [Zustand](https://github.com/pmndrs/zustand) por las siguientes razones:

- **Ligero y minimalista**: No necesita boilerplate ni `reducers`.
- **Reactividad directa**: Cambios al estado actualizan la UI sin necesidad de `useContext` o `Redux`.
- **Persistencia**: Se puede integrar con `localStorage` para mantener sesión activa tras recargas.

El estado global contiene:

- `accessToken`
- `user`
- Métodos como `setToken`, `logout`, etc.

Se accede vía `useAuth()` desde cualquier componente.

---

## Instalación y Ejecución

### Requisitos

- Node.js 18+
- pnpm (recomendado) o npm (usado para este proyecto)

### Instalación

```bash
pnpm install
# o
npm install
```

### Ejecución local

```bash
pnpm run dev
# o
npm run dev
```

### Compilación para producción

```bash
pnpm run build
# o
npm run build
```

El resultado se encuentra en la carpeta `/dist`.

---

## Checklist de Seguridad

- [x] Protección de rutas mediante `RequireAuth`
- [x] Validación de tokens con Zustand
- [x] Flujo de TOTP
- [x] Integración OAuth2 con Google
- [x] Redirección segura en expiración de tokens

---

## Próximas Mejoras

- Integrar pruebas automáticas con Cypress y Jest
- Internacionalización (i18n)
- Prevención de reenvío de formularios
- Soporte para WebAuthn (como 2FA alternativo)

---

## Recursos

- [Zustand](https://github.com/pmndrs/zustand)
- [React Router DOM](https://reactrouter.com/)
- [Google OAuth 2.0](https://developers.google.com/identity)
- [TOTP RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238)

---

¡Listo! Tu frontend ya está preparado para manejar autenticación segura con una arquitectura moderna y extensible.

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ["./tsconfig.node.json", "./tsconfig.app.json"],
      tsconfigRootDir: import.meta.dirname,
    },
  },
});
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    "react-x": reactX,
    "react-dom": reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs["recommended-typescript"].rules,
    ...reactDom.configs.recommended.rules,
  },
});
```
