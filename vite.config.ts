import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "ideogram_tool/static",
    emptyOutDir: true
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:7860",
      "/outputs": "http://127.0.0.1:7860"
    }
  }
});
