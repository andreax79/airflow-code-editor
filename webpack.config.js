const fs = require('fs');
const path = require('path');
const { VueLoaderPlugin } = require("vue-loader");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const autoprefixer = require("autoprefixer");

// Update package.json version number
fs.readFile('./airflow_code_editor/VERSION', 'utf8', (err, version) => {
    fs.readFile('./package.json', (err, data) => {
        if (!err) {
            var packageJsonObj = JSON.parse(data);
            packageJsonObj.version = version.trim();
            packageJsonObj = JSON.stringify(packageJsonObj, null, '  ');
            fs.writeFile('./package.json', packageJsonObj, (err) => {
                if (err) {
                    throw err;
                }
            });
        }
    });
});

module.exports = {
    entry: './src/main.js',
    // mode: 'development',
    mode: 'production',
    output: {
        filename: 'airflow_code_editor.js',
        path: path.resolve(__dirname, 'airflow_code_editor', 'static')
    },
    performance: {
        maxEntrypointSize: 512000,
        maxAssetSize: 512000
    },
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js'
        },
        extensions: ["*", ".js", ".vue", ".json"]
    },
    plugins: [
        new VueLoaderPlugin(),
        new MiniCssExtractPlugin()
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                },
            },
            {
                test: /\.s?css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "null-loader",
                ],
            },
            {
                test: /\.vue$/,
                loader: "vue-loader",
            },
            {
                test: /\.html$/i,
                loader: 'html-loader',
            },
        ],
    }
}
