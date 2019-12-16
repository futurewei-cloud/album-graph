const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ThemesPlugin = require('less-themes-webpack-plugin');
const WebpackMildCompile = require('webpack-mild-compile').Plugin;
const config = require('./graph.config');
const webpack = require('webpack');

module.exports = {
	mode: 'production',
	entry: './scripts/app.js',
	devServer: {
		port: '8082',
		stats: 'errors-only'
	},
	output: {
		path: path.resolve(__dirname, 'dist'),
		filename: 'app.js'
	},
	plugins: [
		new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
		new CleanWebpackPlugin(),
		new HtmlWebpackPlugin({
			title: config.projectName,
			'theme-color': '#000000'
		}),
		new CopyWebpackPlugin([{
			context: 'images/',
			to: 'images/',
			from: '*.png'
		}, {
			context: 'data/',
			from: '*.json'
		}]),
		new ThemesPlugin({
			themesPath: './node_modules/hafgufa/src/themes/moonBeam',
			themes: {
				moonBeam: {
					include: ['light'],
					dark: {
						include: ['dark'],
						mobile: [],
						desktop: ['desktop.less']
					},
					light: {
						mobile: [],
						desktop: ['desktop.less']
					}
				}
			}
		}),
		new WebpackMildCompile()
	],
	module: {
		rules: [{
			test: /\.js$/,
			exclude: /node_modules/,
			use: {
				loader: 'babel-loader'
			}
		}]
	}
};
