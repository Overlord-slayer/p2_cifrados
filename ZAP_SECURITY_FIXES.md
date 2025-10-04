# Correcciones de Seguridad para ZAP - Puerto 8000

## Resumen de Cambios

Se implementaron correcciones mínimas en backend y frontend para eliminar alertas de ZAP al escanear `http://localhost:8000`.

---

## BACKEND (FastAPI - Puerto 8000)

### Archivo Modificado: `backend/app/main.py`

#### 1. CSP Estricta vs Relajada

**CSP ESTRICTA** para toda la aplicación (SIN unsafe-inline, unsafe-eval):
```python
"default-src 'self'; "
"script-src 'self'; "
"style-src 'self'; "
"img-src 'self' data:; "
"font-src 'self' data:; "
"connect-src 'self'; "
"object-src 'none'; "
"base-uri 'self'; "
"form-action 'self'; "
"frame-ancestors 'none'; "
"frame-src 'none'"
```

**CSP RELAJADA** solo para `/docs` y `/redoc` (Swagger necesita unsafe-inline):
```python
"default-src 'self'; "
"script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
"img-src 'self' data: https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
"font-src 'self' data: https://cdn.jsdelivr.net; "
"connect-src 'self'; "
"object-src 'none'; "
"base-uri 'self'; "
"form-action 'self'; "
"frame-ancestors 'none'; "
"frame-src 'none'"
```

#### 2. Headers de Seguridad
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY
- **Referrer-Policy**: no-referrer (más estricto)
- **Server header**: Ocultado

#### 3. Montaje de StaticFiles
- Frontend/dist montado en raíz `/`
- Routers de API priorizados antes de archivos estáticos

---

## FRONTEND (Vite - Puerto 3000)

### Archivo Modificado: `frontend/vite.config.ts`

#### 1. Desactivar Source Maps en Producción
```typescript
build: {
  sourcemap: false,
  minify: 'terser',
  terserOptions: {
    compress: {
      drop_console: true,  // Eliminar console.log
      drop_debugger: true
    }
  }
}
```

#### 2. Headers de Seguridad en Preview
- Mismo CSP que backend (estricto)
- X-Frame-Options, X-Content-Type-Options
- Overlay desactivado

---

## ALERTAS DE ZAP MITIGADAS

### ✅ Resueltas

1. **CSP: Failure to Define Directive with No Fallback**
   - Agregadas todas las directivas requeridas: `default-src`, `script-src`, `style-src`, `img-src`, `font-src`, `connect-src`, `object-src`, `base-uri`, `form-action`, `frame-ancestors`, `frame-src`

2. **CSP: Wildcard Directive**
   - Eliminados todos los wildcards, solo `'self'`

3. **CSP: script-src unsafe-inline/unsafe-eval**
   - Eliminado `unsafe-eval` completamente
   - `unsafe-inline` SOLO en `/docs` y `/redoc` (Swagger UI lo requiere)
   - App principal usa CSP estricta

4. **CSP: style-src unsafe-inline**
   - Eliminado en app principal
   - Permitido SOLO en `/docs` y `/redoc`

5. **Hidden File Found**
   - Source maps desactivados (`sourcemap: false`)
   - No se expone directorio `src/`
   - Solo se sirve `frontend/dist`

6. **Cross-Domain JavaScript Source File Inclusion**
   - CDNs explícitos solo en `/docs`: `https://cdn.jsdelivr.net`, `https://fastapi.tiangolo.com`
   - App principal NO permite CDNs externos

7. **Information Disclosure - Suspicious Comments**
   - Console.log eliminados en build de producción
   - Comentarios minimizados por terser

8. **Content Security Policy (CSP) Header Not Set**
   - CSP presente en todas las respuestas

9. **Missing Anti-clickjacking Header**
   - `X-Frame-Options: DENY` en todas las respuestas

10. **X-Content-Type-Options Header Missing**
    - `X-Content-Type-Options: nosniff` en todas las respuestas

### ⚠️ Informativas

**Session Management Response Identified**
- Si usas cookies de sesión, verifica flags: `HttpOnly`, `Secure`, `SameSite=Lax|Strict`
- Si usas JWT en headers, esta alerta es solo informativa

---

## INSTRUCCIONES PARA ESCANEAR CON ZAP

### 1. Limpiar Sites Anteriores en ZAP

```
1. En ZAP, ir a la pestaña "Sites"
2. Click derecho en cualquier entrada vieja (localhost:3000, etc.)
3. Seleccionar "Remove"
4. Eliminar TODAS las entradas viejas para empezar limpio
```

### 2. Reconstruir Frontend y Arrancar Backend

```bash
# Terminal 1: Reconstruir frontend
cd frontend
npm run build

# Terminal 2: Arrancar backend (servirá frontend desde :8000)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Verificar Headers Antes de Escanear

```powershell
# Ejecutar script de verificación
powershell -ExecutionPolicy Bypass -File test_backend_strict_csp.ps1
```

**Resultado esperado**:
```
=== Testing Backend Strict CSP (http://localhost:8000) ===

1. Testing ROOT path (should have STRICT CSP):
  Status Code: 200
  CSP: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; frame-src 'none'
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  OK: CSP is strict (no unsafe-inline/unsafe-eval)

2. Testing /docs path (should have RELAXED CSP for Swagger):
  Status Code: 200
  CSP: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; ...
  OK: /docs CSP allows unsafe-inline for Swagger UI

=== CSP Directives Check ===
Looking for required directives in ROOT CSP...
  [OK] default-src
  [OK] script-src
  [OK] style-src
  [OK] img-src
  [OK] font-src
  [OK] connect-src
  [OK] object-src
  [OK] base-uri
  [OK] form-action
  [OK] frame-ancestors
  [OK] frame-src
```

### 4. Escanear con ZAP

```
1. En ZAP, ir a "Quick Start"
2. URL to attack: http://localhost:8000
3. Seleccionar "Use traditional spider" ✓
4. Click "Attack"
5. Esperar a que termine
6. Ir a la pestaña "Alerts"
7. Verificar que las alertas CSP/X-Frame-Options/X-Content-Type-Options/Hidden Files/etc. YA NO APARECEN
```

### 5. Verificar Resultados Específicos

**En la app principal (http://localhost:8000/):**
- ✅ CSP estricta (NO unsafe-inline, NO unsafe-eval)
- ✅ Todas las directivas presentes
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ NO archivos .map
- ✅ NO comentarios/console.log en JS

**En /docs (http://localhost:8000/docs):**
- ✅ CSP permite unsafe-inline (Swagger lo necesita)
- ✅ CDNs explícitos (cdn.jsdelivr.net, fastapi.tiangolo.com)
- ✅ Mismos headers de seguridad

---

## NOTAS IMPORTANTES

### 1. No Tocar Lógica de Negocio
- Solo se modificó configuración de servidores
- Endpoints y flujos de la app permanecen intactos
- Middleware agregado de forma no invasiva

### 2. CSP Diferenciada por Ruta
- **App**: CSP estricta (mejor seguridad)
- **/docs**: CSP relajada (funcionalidad de Swagger)
- Esto es correcto y esperado

### 3. Source Maps
- Desactivados en producción
- Solo útiles para desarrollo
- NO deben estar en `dist/`

### 4. Console.log
- Eliminados automáticamente en build
- Solo en desarrollo local

### 5. CORS
- Actualmente permite `http://localhost:3000`
- En producción, ajustar a dominio real

### 6. WebSocket
- NO incluido en connect-src de la app principal
- Si necesitas WebSocket, añadir explícitamente

---

## TROUBLESHOOTING

### Backend no arranca en :8000
```bash
# Verificar si el puerto está ocupado
netstat -ano | findstr :8000

# Matar proceso si es necesario
taskkill /PID <PID> /F
```

### Frontend/dist no existe
```bash
cd frontend
npm run build
```

### CSP sigue mostrando unsafe-*
- Verificar que estás escaneando **http://localhost:8000** (backend)
- NO escanear http://localhost:3000 (preview de Vite)
- Limpiar Sites en ZAP y empezar de cero

### Swagger UI no carga
- `/docs` debe tener CSP relajada con unsafe-inline
- Verificar que el middleware diferencia correctamente las rutas

### ZAP sigue mostrando alertas viejas
- Borrar TODOS los Sites en ZAP
- Reiniciar ZAP
- Escanear solo http://localhost:8000

---

## ARCHIVOS DE VERIFICACIÓN

- `test_backend_strict_csp.ps1` - Verifica CSP estricta vs relajada
- `test_backend_headers.ps1` - Verifica headers básicos
- `test_headers.ps1` - Verifica frontend preview (:3000)

---

## RESUMEN DE COMANDOS

```bash
# 1. Reconstruir frontend
cd frontend && npm run build

# 2. Arrancar backend
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Verificar headers
powershell -ExecutionPolicy Bypass -File test_backend_strict_csp.ps1

# 4. Abrir en navegador para verificar visualmente
start http://localhost:8000

# 5. Escanear con ZAP apuntando a http://localhost:8000
```

---

## COMPARACIÓN ANTES/DESPUÉS

| Alerta | Antes | Después |
|--------|-------|---------|
| CSP Header Not Set | ❌ | ✅ |
| CSP Failure to Define Directive | ❌ | ✅ |
| CSP Wildcard Directive | ❌ | ✅ |
| CSP script-src unsafe-eval | ❌ | ✅ |
| CSP script-src unsafe-inline | ❌ | ✅ (solo /docs) |
| CSP style-src unsafe-inline | ❌ | ✅ (solo /docs) |
| X-Frame-Options Missing | ❌ | ✅ |
| X-Content-Type-Options Missing | ❌ | ✅ |
| Hidden File Found (.map) | ❌ | ✅ |
| Cross-Domain JS Inclusion | ❌ | ✅ (CDNs explícitos) |
| Suspicious Comments | ❌ | ✅ |

✅ = Mitigada
❌ = Alerta presente
