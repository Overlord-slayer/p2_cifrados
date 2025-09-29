import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Security headers and build configuration
  build: {
    sourcemap: false, // Disable sourcemaps in production for security
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true, // Remove debugger statements
      },
    },
  },

  // Development server configuration
  server: {
    open: false, // Don't auto-open browser for security
    strictPort: true,
    host: 'localhost', // Bind only to localhost for security
    cors: {
      origin: ['http://localhost:3000', 'http://localhost:5173'],
      credentials: true,
    },
  },

  // Preview server configuration (for production builds)
  preview: {
    port: 4173,
    host: 'localhost',
    strictPort: true,
    open: false,
  },

  // Security: Remove development overlay in production
  define: {
    'process.env.NODE_ENV': '"production"',
  },

  /**
   * Areas para agreagar nuevos aliases segun se necesiten
   */
  resolve: {
    alias: [
      {
        find: "@pages",
        replacement: resolve("./src/pages"),
      },
      {
        find: "@components",
        replacement: resolve("./src/components"),
      },
      {
        find: "@api",
        replacement: resolve("./src/lib"),
      },
      {
        find: "@store",
        replacement: resolve("./src/store"),
      },
      {
        find: "@constants",
        replacement: resolve("./src/constants"),
      },
      {
        find: "@routes",
        replacement: resolve("./src/routes"),
      },
    ],
  },
});
