import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // When the Django backend (Day 2) runs on :8000, /api goes to it.
      "/api": "http://localhost:8000",
    },
  },
});
