import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  base: '/',
  // Reutiliza los assets del proyecto principal (fonts, FA, images)
  publicDir: resolve(__dirname, '../CDS_VUE3_ZERO/public'),
})
