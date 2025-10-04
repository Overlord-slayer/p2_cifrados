# Configuración de Seguridad Backend (FastAPI)

## Resumen

Se añadió middleware de cabeceras de seguridad y montaje de StaticFiles para que ZAP pueda escanear `http://localhost:8000` sin alertas de seguridad.

## Cambios Realizados

### Archivo: `backend/app/main.py`

#### 1. Importaciones Añadidas
```python
from fastapi.staticfiles import StaticFiles
```

#### 2. Middleware de Seguridad Actualizado
Se actualizó `SecurityHeadersMiddleware` con las cabeceras requeridas para ZAP:

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self' data:; "
    "connect-src 'self' ws://localhost:8000; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'"
)
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
```

#### 3. Montaje de Frontend Build
Se añadió montaje de `frontend/dist` en la ruta raíz:

```python
dist_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.isdir(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
```

Esto permite:
- Servir la build de producción del frontend en `http://localhost:8000/`
- La ruta raíz responde con 200 (no 404)
- ZAP puede escanear la aplicación completa

#### 4. CORS Configurado
CORS ya estaba configurado para desarrollo local:
```python
allow_origins=["http://localhost:3000"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

## Verificación de Cabeceras

### Script de Prueba
Se creó `test_backend_headers.ps1` que verifica:

1. Cabeceras de seguridad en la raíz (`/`)
2. Funcionamiento del endpoint `/docs`

**Ejecutar**:
```powershell
powershell -ExecutionPolicy Bypass -File test_backend_headers.ps1
```

### Resultado de Verificación

```
=== Testing Backend Security Headers (http://localhost:8000) ===

Status Code: 200

Security Headers:
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' ws://localhost:8000; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer-when-downgrade
```

✅ Todas las cabeceras de seguridad presentes
✅ Ruta raíz responde 200
✅ Frontend servido desde backend

## Alertas de ZAP Resueltas

✅ **Content Security Policy (CSP) Header Not Set**
- CSP configurado con políticas restrictivas

✅ **Missing Anti-clickjacking Header**  
- `X-Frame-Options: DENY` presente

✅ **X-Content-Type-Options Header Missing**
- `X-Content-Type-Options: nosniff` presente

## Uso

### Iniciar Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- **Frontend**: `http://localhost:8000/` (servido desde dist)
- **API**: `http://localhost:8000/api/*`
- **Docs**: `http://localhost:8000/docs`

### Escanear con ZAP

1. Asegurar que el backend está corriendo en puerto 8000
2. Asegurar que existe `frontend/dist` (ejecutar `npm run build` si es necesario)
3. Configurar ZAP para escanear: `http://localhost:8000`
4. Verificar que las alertas CSP/X-Frame-Options/X-Content-Type-Options no aparecen

## Configuración de Seguridad

### Content-Security-Policy
```
default-src 'self'              - Solo recursos del mismo origen
script-src 'self'               - Scripts solo del mismo origen
style-src 'self' 'unsafe-inline' - Estilos del mismo origen + inline
img-src 'self' data:            - Imágenes del mismo origen + data URIs
font-src 'self' data:           - Fuentes del mismo origen + data URIs
connect-src 'self' ws://localhost:8000 - Conexiones + WebSocket
object-src 'none'               - No objetos/embeds
base-uri 'self'                 - Base URI solo del mismo origen
frame-ancestors 'none'          - No puede ser embebido en frames
```

### X-Frame-Options
```
DENY - No permite que la página sea embebida en frames/iframes
```

### X-Content-Type-Options
```
nosniff - Previene MIME type sniffing
```

### Referrer-Policy
```
no-referrer-when-downgrade - Política de referrer estándar
```

## Estructura de la Aplicación

```
backend/
├── app/
│   ├── main.py              <- Middleware y configuración de seguridad
│   ├── routers/             <- Endpoints de la API
│   ├── endpoints/           <- Endpoints adicionales
│   └── middleware/          <- Middleware personalizado
frontend/
└── dist/                    <- Build de producción (montado en backend:8000)
```

## Notas Importantes

1. **StaticFiles se monta DESPUÉS de los routers**: Esto asegura que las rutas de API (`/api/*`, `/docs`, etc.) se prioricen sobre los archivos estáticos.

2. **Cabeceras en todas las respuestas**: El middleware aplica las cabeceras a todas las respuestas, incluyendo API, archivos estáticos y docs.

3. **CORS para desarrollo**: Configurado para `localhost:3000` (frontend dev). En producción, ajustar según necesidad.

4. **CSP permite WebSocket**: `connect-src 'self' ws://localhost:8000` para permitir conexiones WebSocket si son necesarias.

5. **Sin tocar lógica de negocio**: Solo se añadió configuración de servidor. Los endpoints y flujos de la aplicación permanecen intactos.

## Troubleshooting

### frontend/dist no existe
Si el directorio no existe, el backend iniciará sin problema pero:
- La ruta `/` no estará disponible (404)
- Solo las rutas de API funcionarán
- Construir frontend: `cd frontend && npm run build`

### Puerto 8000 ocupado
Cambiar el puerto en el comando uvicorn:
```bash
uvicorn app.main:app --port 8001
```

### Cabeceras no aparecen
Verificar que:
1. El servidor backend está corriendo
2. El middleware `SecurityHeadersMiddleware` está añadido
3. Usar el script de verificación para confirmar

### CORS bloqueando requests
Si necesitas permitir más orígenes en desarrollo:
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

## Verificación curl

Para verificar manualmente las cabeceras:

```bash
curl -I http://localhost:8000/
```

Deberías ver las cuatro cabeceras de seguridad en la respuesta.
