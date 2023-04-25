import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

// https://vitejs.dev/config/
export default defineConfig({
    ...(process.env.NODE_ENV === 'development'
        ? {
              define: {
                  global: {}
              }
          }
        : {}),
    server: {
        port: 8080
    },
    plugins: [vue(), vuetify({ autoImport: true })],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
            ...(process.env.NODE_ENV !== 'development'
                ? {
                      './runtimeConfig': './runtimeConfig.browser' //fix production build
                  }
                : {})
        }
    }
})
