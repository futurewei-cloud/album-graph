module.exports = function(api) {
	const presets = [
		[
			'@babel/preset-env', {
			'targets': {
				'node': 'current'
			}
		}
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
