module.exports = function(api) {
	const presets = [
		[
			'@babel/preset-env'
		]
	];
	const plugins = [
		'lodash'
	];

	api.cache(true);

	return {
		presets,
		plugins
	};
};
