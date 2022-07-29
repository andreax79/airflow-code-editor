import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    build: {
        emptyOutDir: false,
        outDir: 'airflow_code_editor/static',
        rollupOptions: {
            input: {
                app: 'src/index.html'
            },
            output: {
                entryFileNames: 'airflow_code_editor.js',
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name == 'src/index.css') {
                        return 'css/style.css';
                    }
                    return assetInfo.name;
                },
            },
        },
    }
})
