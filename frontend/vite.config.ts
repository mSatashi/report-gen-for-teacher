import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  envDir: '../',
  plugins: [react(), {
    name: 'html-transform',
    transformIndexHtml(html) {
      return html.replace('%META_TITLE%', 'Report GenAI Otomatis')
    },
  }],
  preview:{
    allowedHosts: ['localhost', 'app.anfaresi.com']
  }
})
