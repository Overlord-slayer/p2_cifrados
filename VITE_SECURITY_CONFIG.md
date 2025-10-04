# Configuración de Seguridad para Vite Preview Server

## Resumen

Se ha configurado el servidor de preview de Vite para eliminar las alertas de seguridad de ZAP escaneando en el puerto 3000.

## Cambios Realizados

### 1. Archivo `frontend/vite.config.ts`

Se han añadido las siguientes configuraciones:

#### Servidor de Desarrollo (dev)
- **Puerto**: 5173 (por defecto)
- **Overlay desactivado**: `overlay: false` - No expone rutas/stack traces
- **Headers de seguridad**:
  - `Content-Security-Policy`: Incluye `connect-src 'self' ws://localhost:5173` para permitir WebSocket HMR
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`

#### Servidor de Preview (producción)
- **Puerto**: 3000 (configurado para ZAP)
- **strictPort**: true (falla si el puerto no está disponible)
- **Headers de seguridad**:
  - `Content-Security-Policy: default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
- **Protección de rutas**: Proxy que bloquea rutas `/@vite/*` retornando 404

## Uso

### Para Desarrollo (con HMR)
```bash
cd frontend
npm run dev
```
El servidor correrá en `http://localhost:5173` con HMR activo.

### Para Preview/Producción (para escaneo ZAP)
```bash
cd frontend
npm run build
npm run preview
```
El servidor correrá en `http://localhost:3000` sin HMR, listo para escaneo de seguridad.

## Verificación de Headers

Se ha incluido un script de verificación `test_headers.ps1` que prueba:

1. Presencia de los tres headers de seguridad
2. Bloqueo de rutas `/@vite/client`

**Ejecutar verificación**:
```powershell
powershell -ExecutionPolicy Bypass -File test_headers.ps1
```

**Resultado esperado**:
```
=== Security Headers Test ===

Content-Security-Policy: default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff

=== Testing /@vite/client route (should be blocked) ===
Error (Expected): 404
```

## Alertas de ZAP Resueltas

✅ **Content Security Policy (CSP) Header Not Set**
- Se añadió header CSP con políticas restrictivas

✅ **Missing Anti-clickjacking Header**
- Se añadió `X-Frame-Options: DENY`

✅ **X-Content-Type-Options Header Missing**
- Se añadió `X-Content-Type-Options: nosniff`

✅ **XSS en /@vite/client**
- Ruta bloqueada en preview, retorna 404

## Notas Importantes

1. **Preview vs Dev**: El modo preview NO tiene HMR ni overlay. Es la build de producción servida localmente.

2. **CSP en Dev**: En modo dev se permite `connect-src ws://localhost:5173` para WebSocket de HMR.

3. **CSP en Preview**: En preview NO se permite WebSocket ya que no hay HMR.

4. **Rutas Vite**: Las rutas `/@vite/*` solo existen en modo dev. En preview están bloqueadas.

5. **Lógica de la App**: No se tocó ningún endpoint ni flujo de la aplicación. Solo configuración de servidor.

## Configuración de Seguridad Aplicada

### Content-Security-Policy
```
default-src 'self'        - Solo recursos del mismo origen
object-src 'none'         - No permite objetos/embeds
base-uri 'self'          - Base URI solo del mismo origen
frame-ancestors 'none'   - No puede ser embebido en frames
```

### X-Frame-Options
```
DENY - No permite que la página sea embebida en ningún frame/iframe
```

### X-Content-Type-Options
```
nosniff - Previene MIME type sniffing
```

## Escaneo con ZAP

Para escanear con ZAP:

1. Construir el proyecto:
   ```bash
   cd frontend
   npm run build
   ```

2. Iniciar preview en puerto 3000:
   ```bash
   npm run preview
   ```

3. Configurar ZAP para escanear:
   - URL: `http://localhost:3000`
   - Verificar que las alertas anteriores ya no aparezcan

## Troubleshooting

### Puerto 3000 ocupado
Si el puerto 3000 está en uso, el servidor fallará por `strictPort: true`. 
Liberar el puerto o modificar `preview.port` en `vite.config.ts`.

### Headers no aparecen
Verificar que estés usando `npm run preview` y no `npm run dev`.
El servidor dev usa puerto 5173 y tiene configuración diferente.

### Rutas /@vite/ aparecen
Esto solo puede ocurrir en modo dev. En preview están bloqueadas.
