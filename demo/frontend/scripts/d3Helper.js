const d3Helper = {
	dropShadow(defs, id, dx = 1, dy = 1, blurRadius = 4, spread = 0, opacity = 1, color = '#000000') {
		const filter = defs.append('filter')
			.attr('id', id)
			.attr('x', '-5000%')
			.attr('y', '-5000%')
			.attr('width', '10000%')
			.attr('height', '10000%');

		filter.append('feFlood')
			.attr('flood-color', color)
			.attr('flood-opacity', opacity)
			.attr('result', 'flooded');

		filter.append('feComposite')
			.attr('in', 'flooded')
			.attr('in2', 'SourceGraphic')
			.attr('operator', 'in')
			.attr('result', 'mask');

		filter.append('feOffset')
			.attr('in', 'mask')
			.attr('dx', dx)
			.attr('dy', dy)
			.attr('result', 'offset');

		filter.append('feMorphology')
			.attr('in', 'offset')
			.attr('operator', 'dilate')
			.attr('radius', spread)
			.attr('result', 'dilated');

		filter.append('feGaussianBlur')
			.attr('in', 'dilated')
			.attr('stdDeviation', blurRadius)
			.attr('result', 'blurred');

		const feMerge = filter.append('feMerge');
		feMerge.append('feMergeNode')
			.attr('in', 'blurred');
		feMerge.append('feMergeNode')
			.attr('in', 'SourceGraphic');
	}
};

export default d3Helper;
