import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Desactivar source maps en producción
  build: {
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Eliminar console.log en producción
        drop_debugger: true
      }
    }
  },
  // Configuración de servidor dev: desactivar overlay y añadir headers de seguridad
  server: {
    port: 5173,
    hmr: {
      overlay: false // Desactivar overlay para no exponer rutas/stack traces
    },
    headers: {
      'Content-Security-Policy': "default-src 'self'; connect-src 'self' ws://localhost:5173; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff'
    }
  },
  // Configuración de preview: puerto 3000 con headers de seguridad
  preview: {
    port: 3000,
    strictPort: true,
    headers: {
      'Content-Security-Policy': "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff'
    },
    // Middleware para bloquear rutas de Vite dev en preview
    proxy: {
      '/@vite': {
        target: 'http://localhost:3000',
        configure: (proxy, options) => {
          proxy.on('error', () => {});
          proxy.on('proxyReq', (proxyReq, req, res) => {
            res.statusCode = 404;
            res.end();
          });
        }
      }
    }
  },
  /**
   * Areas para agreagar nuevos aliases segun se necesiten
   */
  resolve: {
    alias: [
      {
        find: "@pages",
        replacement: resolve(__dirname, "./src/pages"),
      },
      {
        find: "@components",
        replacement: resolve(__dirname, "./src/components"),
      },
      {
        find: "@api",
        replacement: resolve(__dirname, "./src/lib"),
      },
      {
        find: "@store",
        replacement: resolve(__dirname, "./src/store"),
      },
      {
        find: "@constants",
        replacement: resolve(__dirname, "./src/constants"),
      },
      {
        find: "@routes",
        replacement: resolve(__dirname, "./src/routes"),
      },
    ],
  },
});
