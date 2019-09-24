export const eachPair = (array, callback) => {
	let i;
	let j;
	const length = array.length;
	let doBreak = false;

	for (i = 0; i < length; i++) {
		for (j = i + 1; j < length; j++) {
			if (callback(array[i], array[j])) {
				doBreak = true;
				break;
			}
		}

		if (doBreak) {
			break;
		}
	}
};

export const isLinkInBounds = (link, bounds) => {
	return !((link.source.x < bounds.minX && link.target.x < bounds.minX) || (link.source.x > bounds.maxX && link.target.x > bounds.maxX) || (link.source.y < bounds.minY && link.target.y < bounds.minY) || (link.source.y > bounds.maxY && link.target.y > bounds.maxY));
};

export const hypot = (x, y) => Math.sqrt(x * x + y * y);

export const updateLine = (link, line, bounds, linkContainer) => {
	if (!bounds || isLinkInBounds(link, bounds)) {
		if (!line.parentNode) {
			linkContainer.appendChild(line);
		}
		const lineOffsetX = link.source.x - link.target.x;
		const lineOffsetY = link.source.y - link.target.y;
		const lineDistance = hypot(lineOffsetX, lineOffsetY);

		if (!isNaN(lineDistance)) {
			line.setAttribute('x1', link.source.x + lineOffsetX * -link.source.rPlus / lineDistance);
			line.setAttribute('y1', link.source.y + lineOffsetY * -link.source.rPlus / lineDistance);
			line.setAttribute('x2', link.target.x + lineOffsetX * link.target.rPlus / lineDistance);
			line.setAttribute('y2', link.target.y + lineOffsetY * link.target.rPlus / lineDistance);
			if (link.width) {
				line.style.strokeWidth = link.width + 'px';
			}
		}

		return true;
	}
	else {
		if (line.parentNode) {
			line.parentNode.removeChild(line);
		}

		return false;
	}
};
