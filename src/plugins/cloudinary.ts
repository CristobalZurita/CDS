/**
 * Plugin Cloudinary para Vue 3
 * Configuración global del SDK oficial
 */

import { Cloudinary } from '@cloudinary/url-gen'
import { type App } from 'vue'

// Instancia de Cloudinary con tu cloud name
const cld = new Cloudinary({
  cloud: {
    cloudName: 'dgwwi77ic'
  },
  url: {
    secure: true
  }
})

// Plugin para Vue
export default {
  install(app: App) {
    app.config.globalProperties.$cld = cld
    app.provide('cloudinary', cld)
  }
}

export { cld }
