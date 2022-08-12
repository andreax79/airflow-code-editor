import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFile, writeFile } from 'fs';

// Update package.json version number
readFile('./airflow_code_editor/VERSION', 'utf8', (err, version) => {
    readFile('./package.json', (err, packageData) => {
        if (!err) {
            const packageJsonObj = JSON.parse(packageData);
            packageJsonObj.version = version.trim();
            const data = JSON.stringify(packageJsonObj, null, '  ');
            writeFile('./package.json', data, (err) => {
                if (err) {
                    throw err;
                }
            });
        }
    });
});

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    build: {
        sourcemap: true,
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
