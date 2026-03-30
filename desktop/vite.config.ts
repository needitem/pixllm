import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'node:path';

export default defineConfig({
  root: path.resolve('src/renderer'),
  base: './',
  plugins: [svelte()],
  build: {
    outDir: path.resolve('dist/renderer'),
    emptyOutDir: true
  },
  server: {
    port: 4173,
    strictPort: true
  }
});
