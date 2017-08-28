const webpack = require('webpack')
const path = require('path')

module.exports = (env = {}) => {

    // Variables set by npm scripts in package.json
    const isProduction = env.production === true
    const platform = env.platform // 'default' by default
    return {
        entry: {
            main: [
                './src/index.js'
            ]
        },
        output: {
            path: __dirname,
            publicPath: '/',
            filename: 'bundle.js'
        },
        module: {
            rules: [
                {
                  test: /\.js$/,
                  loader: 'babel-loader',
                  exclude: /node_modules/
                },
                {
                  test: /\.html$/,
                  loader: 'html-loader'
                },
                {
                  test: /\.css$/,
                  use: [
                    { loader: 'style-loader' },
                    { loader: 'css-loader' }
                  ]
                },
                {
                  test: /\.(png|gif|jpg)$/,
                  loader: 'url-loader',
                  options: { limit: '25000' }
                },
                {
                  test: /\.(ttf|eot|svg)$/,
                  loader: 'file-loader'
                }
            ]
        },
        devServer: {
            port : 9000,
            historyApiFallback: true,
            contentBase: './'
        }
    }
};
