import { fileURLToPath, URL } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Where the FastAPI backend lives from the point of view of the Vite server.
// Inside docker-compose it is the `web` service; outside Docker, override it.
const API_TARGET: string = process.env.VITE_API_PROXY_TARGET ?? "http://web:8000";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "0.0.0.0", // reachable from outside the container
    port: 5173,
    proxy: {
      // The browser only ever talks to the frontend origin. Anything under /api
      // is forwarded to the backend with the /api prefix removed
      // (/api/auth/me -> http://web:8000/auth/me), so cookies stay same-origin.
      "/api": {
        target: API_TARGET,
        changeOrigin: false,
        rewrite: (path: string): string => path.replace(/^\/api/, ""),
      },
    },
  },
});
