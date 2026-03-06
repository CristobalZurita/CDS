import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import imagemin from 'vite-plugin-imagemin'

// https://vitejs.dev/config/
export default defineConfig({
    // Para dominio propio: '/'
    base: '/',
    plugins: [
        vue(),
        // Image optimization: compress images during build
        imagemin({
            gifsicle: { optimizationLevel: 7 },
            optipng: { optimizationLevel: 7 },
            mozjpeg: { quality: 20, progressive: true },
            pngquant: { quality: [0.8, 0.9], speed: 4 },
            svgo: {
                plugins: [
                    { name: 'removeViewBox' },
                    { name: 'removeEmptyAttrs' },
                ],
            },
        }),
    ],
    
    // Configuración del alias @ para resolver rutas
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    
    // Proxy: Frontend → Backend
    server: {
        host: '0.0.0.0',
        port: 5173,
        strictPort: false,
        // Avoid scanning or watching vendored MODELOS subprojects
        watch: {
            ignored: [
                '**/MODELOS/**',
                '**/backend/.venv/**',
                '**/backend/**/__pycache__/**',
                '**/.venv/**',
            ]
        },
        optimizeDeps: {
            // limit dependency scanning to the primary index
            entries: ['./index.html']
        },
        proxy: {
            // Cualquier request a /api se reenvía al backend
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
                rewrite: (path) => path.replace(/^\/api/, '/api')
            }
        }
    },
    
    css: {
        preprocessorOptions: {
            scss: {
                api: 'modern-compiler',
                silenceDeprecations: ["legacy-js-api", "color-functions", "global-builtin", "import"],
            },
        },
    },

    build: {
        // Code splitting para chunks menores
        rollupOptions: {
            output: {
                manualChunks: {
                    // Vendor libraries
                    vue: ['vue', 'vue-router', 'pinia'],
                    ui: ['bootstrap', '@fortawesome/fontawesome-free'],
                    utils: ['axios', 'dompurify'],
                },
            },
        },
        // Minify agresivamente
        minify: 'terser',
        terserOptions: {
            compress: {
                drop_console: true,
                drop_debugger: true,
            },
        },
        // Reportar chunks grandes
        chunkSizeWarningLimit: 600,
        // Reporte detallado
        reportCompressedSize: true,
    },

    // Critical CSS inlining (Critters)
    // Automatically inlines critical CSS in HTML head
    // and defers non-critical CSS
    html: {
        minify: false, // Vite handles HTML minification separately
    },
})
