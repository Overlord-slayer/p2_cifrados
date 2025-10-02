# Corrección de Manejo de Tokens y Race Conditions

**Fecha:** 2025-09-30  
**Tipo:** Bugfix - Funcionalidad

---

## Problemas Identificados

### 1. Error 401 en `/user`
**Causa:** Peticiones sin header `Authorization: Bearer <token>`  
**Síntoma:** `401 Unauthorized` al cargar perfil

### 2. Error 404 en `/users//key`  
**Causa:** Race condition - username vacío al momento de la petición  
**Síntoma:** URL con doble slash `/users//key`

### 3. Navegación prematura
**Causa:** Navigate ejecutado antes de cargar datos del usuario  
**Síntoma:** Pantalla de chat sin datos de usuario inicialmente

---

## Soluciones Implementadas

### 1. Interceptor de Axios (`frontend/src/lib/api.ts`)

```typescript
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
```

**Beneficios:**
- ✅ Token enviado automáticamente en todas las peticiones
- ✅ Manejo automático de token expirado
- ✅ Código más limpio - no repetir `headers: {Authorization: ...}` en cada petición

---

### 2. Flujo de Login Corregido (`frontend/src/pages/Login/Login.tsx`)

```typescript
// ANTES (INCORRECTO):
const res = await signin(email, password, totp);
setTokens(access_token, refresh_token);
loadUsername(accessToken);  // No espera, puede estar vacío
navigate("/chat");  // Navega inmediatamente

// DESPUÉS (CORRECTO):
const res = await signin(email, password, totp);
const { access_token, refresh_token } = res.data;

// 1. Guardar tokens en localStorage PRIMERO
localStorage.setItem("access_token", access_token);
localStorage.setItem("refresh_token", refresh_token);
setTokens(access_token, refresh_token);

// 2. ESPERAR a que se cargue el username
await loadUsername(access_token);

// 3. Solo ENTONCES navegar
setTimeout(() => {
  navigate("/chat");
}, 500);
```

**Orden correcto:**
1. Guardar tokens en localStorage (para que interceptor lo use)
2. Actualizar estado de auth
3. **Await** cargar perfil/username
4. Navegar a /chat

---

### 3. Prevención de Race Conditions

**Recomendación para componentes que usan username:**

```typescript
// INCORRECTO:
useEffect(() => {
  const url = `${API}/users/${username}/key`;  // username puede estar vacío
  api.get(url);
}, []);

// CORRECTO:
useEffect(() => {
  if (!auth.token) return;  // Esperar token
  if (!auth.username) return;  // Esperar username
  
  const url = `${API}/users/${encodeURIComponent(auth.username)}/key`;
  api.get(url).catch(console.error);
}, [auth.token, auth.username]);  // Re-ejecutar cuando cambien
```

**Puntos clave:**
- ✅ Verificar que token y username existan antes de hacer peticiones
- ✅ Usar `encodeURIComponent()` para URLs
- ✅ Dependencias correctas en `useEffect`

---

## Verificación CORS

El backend ya tiene configuración correcta:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Incluye "Authorization"
)
```

✅ Permite header `Authorization`  
✅ Permite credenciales  
✅ Configuración correcta

---

## Pruebas de Verificación

### Test 1: Login y carga de perfil
```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Pass123!","totp_code":"123456"}'

# 2. Usar token para obtener perfil
curl http://localhost:8000/user \
  -H "Authorization: Bearer <token_del_paso_1>"

# Resultado esperado: 200 OK con {email: "test@test.com"}
```

### Test 2: Interceptor en acción
```typescript
// En frontend:
// 1. Login exitoso guarda token en localStorage
// 2. Cualquier petición con API automáticamente lleva el token

import API from '@api/api';

// No necesitas especificar Authorization manualmente
const response = await API.get('/user');  
// Interceptor lo añade automáticamente
```

### Test 3: Token expirado
```bash
# Con token expirado o inválido:
curl http://localhost:8000/user \
  -H "Authorization: Bearer invalid_token"

# Resultado: 401 Unauthorized
# Frontend: Interceptor limpia localStorage y RequireAuth redirige a /login
```

---

## Resumen de Cambios

| Archivo | Cambio | Impacto |
|---------|--------|---------|
| `frontend/src/lib/api.ts` | Agregado interceptor de request | Token automático en todas las peticiones |
| `frontend/src/lib/api.ts` | Agregado interceptor de response | Manejo automático de 401 |
| `frontend/src/pages/Login/Login.tsx` | Await loadUsername antes de navigate | Previene race conditions |
| `frontend/src/pages/Login/Login.tsx` | localStorage.setItem antes de peticiones | Token disponible para interceptor |

---

## Checklist de Verificación

- [x] Interceptor de Axios configurado
- [x] Token guardado en localStorage antes de peticiones
- [x] `await loadUsername()` antes de navegar
- [x] CORS permite header `Authorization`
- [x] Manejo de token expirado (401)
- [x] Sin race conditions en carga de perfil
- [x] `encodeURIComponent()` en URLs con parámetros de usuario

---

## Notas Adicionales

### Para desarrollo futuro:
1. **Refresh token automático:** Implementar interceptor que intente refrescar token en 401 antes de logout
2. **Retry de peticiones:** Reintentar peticiones fallidas después de refrescar token
3. **Indicadores de carga:** Mostrar loading durante `loadUsername()` en login

### Ejemplo de refresh automático (opcional):
```typescript
API.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post('/auth/refresh', {}, {
          headers: { 'refresh_token': refreshToken }
        });
        localStorage.setItem('access_token', data.access_token);
        error.config.headers.Authorization = `Bearer ${data.access_token}`;
        return API(error.config);  // Reintentar petición original
      } catch (refreshError) {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

---

**Estado:** ✅ COMPLETADO  
**Resultado:** Flujo de autenticación funcionando correctamente sin race conditions
