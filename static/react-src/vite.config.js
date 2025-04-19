const { defineConfig } = require('vite');
const react = require('@vitejs/plugin-react');

module.exports = defineConfig({
  plugins: [react()],
  build: {
    outDir: '../dist', // Output build to static/dist
    emptyOutDir: false,
  },
  server: {
    port: 5173,
  },
});
