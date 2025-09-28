import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
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
  // Security and production configuration
  build: {
    minify: true,
    sourcemap: false, // Disable source maps in production for security
  },
  server: {
    // Development server configuration
    hmr: {
      overlay: process.env.NODE_ENV === 'development', // Only show overlay in development
    },
  },
  define: {
    // Remove development tools and debugging info in production
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
  },
  // Remove console logs in production build
  esbuild: process.env.NODE_ENV === 'production' ? {
    drop: ['console', 'debugger'],
  } : {},
});
