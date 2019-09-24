const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ThemesPlugin = require('less-themes-webpack-plugin');
const HtmlWebpackIncludeAssetsPlugin = require('html-webpack-include-assets-plugin');
const WebpackMildCompile = require('webpack-mild-compile').Plugin;
const config = require('./graph.config');

module.exports = {
	entry: './scripts/app.js',
	devServer: {
		host: '0.0.0.0',
		port: '8082'
	},
	output: {
		path: path.resolve(__dirname, 'dist'),
		filename: 'app.js'
	},
	plugins: [
		new CleanWebpackPlugin(['dist']), new HtmlWebpackPlugin({
			title: config.projectName
		}), new CopyWebpackPlugin([
			{
				context: 'images/',
				to: 'images/',
				from: '*.png'
			}, {
				context: 'data/',
				from: '*.json'
			}
		]), new ThemesPlugin({
			themesPath: './node_modules/hafgufa/src/ui/themes/moonBeam',
			themes: {
				moonBeam: {
					dark: {
						mobile: ['light.less', 'dark.less'],
						desktop: ['light.less', 'dark.less', 'desktop.less']
					},
					light: {
						mobile: ['light.less'],
						desktop: ['light.less', 'desktop.less']
					}
				}
			}
		}), new WebpackMildCompile()
	],
	module: {
		rules: [
			{
				test: /\.js$/,
				exclude: /node_modules/,
				use: {
					loader: 'babel-loader'
				}
			}
		]
	},
	stats: {
		colors: true
	}
};
