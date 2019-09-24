import { Enum, method, Vector } from 'type-enforcer';
import './Links.less';

const LINK_STYLES = new Enum({
	LINE: 'line',
	ARROW: 'arrow',
	ARROW_FROM: 'arrow_from',
	TRIANGLE: 'triangle',
	TRIANGLE_FROM: 'triangle_from',
	STRETCH: 'stretch',
	STRETCH_FROM: 'stretch_from'
});

const ninety = Math.PI / 2;

const setLinkOffset = function() {
	this[OFFSET_SIZE] = this.maxLinkSize() - this.minLinkSize();
};

const hypot = (x, y) => Math.sqrt(x * x + y * y);

const isLinkInBounds = (link, bounds) => {
	if (isNaN(link.source.x) || isNaN(link.target.x) || isNaN(link.source.y) || isNaN(link.target.y)) {
		return false;
	}
	if (link.source.x < bounds.minX && link.target.x < bounds.minX) {
		return false;
	}
	if (link.source.x > bounds.maxX && link.target.x > bounds.maxX) {
		return false;
	}
	if (link.source.y < bounds.minY && link.target.y < bounds.minY) {
		return false;
	}
	return !(link.source.y > bounds.maxY && link.target.y > bounds.maxY);
};

const drawLine = (vector, width) => {
	const sideways = new Vector(vector.start(), vector.end());
	sideways.angle(sideways.angle() + ninety).length(width / 2);
	const shift = sideways.start().subtract(sideways.end());

	const point1 = vector.start().add(shift).toString();
	const point2 = vector.end().add(shift).toString();
	const point3 = vector.end().subtract(shift).toString();
	const point4 = vector.start().subtract(shift).toString();

	return `M ${point1} L${point2} ${point3} ${point4}z`;
};

const drawArrow = (vector, width) => {
	const sideways = new Vector(vector.start(), vector.end());
	sideways.angle(sideways.angle() + ninety).length(width / 2);
	const shiftInner = sideways.start().subtract(sideways.end());
	sideways.length(width * 2);
	const shiftOuter = sideways.start().subtract(sideways.end());

	const arrowHeadVector = new Vector(vector.end(), vector.start());
	arrowHeadVector.length(width * 6);

	const point1 = vector.start().add(shiftInner).toString();
	const point2 = arrowHeadVector.end().add(shiftInner).toString();
	const point3 = arrowHeadVector.end().add(shiftOuter).toString();
	const point4 = vector.end().toString();
	const point5 = arrowHeadVector.end().subtract(shiftOuter).toString();
	const point6 = arrowHeadVector.end().subtract(shiftInner).toString();
	const point7 = vector.start().subtract(shiftInner).toString();

	return `M ${point1} L${point2} ${point3} ${point4} ${point5} ${point6} ${point7}z`;
};

const drawTriangle = (vector, width) => {
	const sideways = new Vector(vector.start(), vector.end());
	sideways.angle(sideways.angle() + ninety).length(width / 2);
	const shiftStart = sideways.start().subtract(sideways.end());

	const point1 = vector.start().add(shiftStart).toString();
	const point2 = vector.end().toString();
	const point3 = vector.start().subtract(shiftStart).toString();

	return `M ${point1} L${point2} ${point3}z`;
};

const drawStretch = (vector, width) => {
	const sideways = new Vector(vector.start(), vector.end());
	sideways.angle(sideways.angle() + ninety).length(width / 2);
	const shiftStart = vector.start().subtract(sideways.end());
	sideways.length(0.25);
	const shiftEnd = vector.start().subtract(sideways.end());

	const point1 = vector.start().add(shiftStart).toString();
	const point2 = vector.start().add(shiftEnd).toString();
	const point3 = vector.end().add(shiftEnd).toString();
	const point4 = vector.end().subtract(shiftEnd).toString();
	const point5 = vector.start().subtract(shiftEnd).toString();
	const point6 = vector.start().subtract(shiftStart).toString();

	return `M ${point1} C${point1} ${point2} ${point3} L${point4} C${point5} ${point6} ${point6}z`;
};

const updateLine = (link, element, bounds, linkContainer, style) => {
	if (!bounds || isLinkInBounds(link, bounds)) {
		if (!element.parentNode) {
			linkContainer.appendChild(element);
		}
		const lineOffsetX = link.source.x - link.target.x;
		const lineOffsetY = link.source.y - link.target.y;
		const lineDistance = hypot(lineOffsetX, lineOffsetY);

		if (!isNaN(lineDistance)) {
			let path;
			let vector = new Vector(link.source, link.target);

			vector.length(vector.length() - link.target.rPlus);
			vector.invert();
			vector.length(vector.length() - link.source.rPlus);
			vector.invert();

			if (style === LINK_STYLES.LINE) {
				path = drawLine(vector, link.width);
			}
			else if (style === LINK_STYLES.ARROW) {
				path = drawArrow(vector, link.width);
			}
			else if (style === LINK_STYLES.ARROW_FROM) {
				vector.invert();
				path = drawArrow(vector, link.width);
			}
			else if (style === LINK_STYLES.TRIANGLE) {
				path = drawTriangle(vector, link.width);
			}
			else if (style === LINK_STYLES.TRIANGLE_FROM) {
				vector.invert();
				path = drawTriangle(vector, link.width);
			}
			else if (style === LINK_STYLES.STRETCH) {
				path = drawStretch(vector, link.width);
			}
			else if (style === LINK_STYLES.STRETCH_FROM) {
				vector.invert();
				path = drawStretch(vector, link.width);
			}

			element.setAttribute('d', path);
		}

		return true;
	}
	else {
		if (element.parentNode) {
			element.parentNode.removeChild(element);
		}

		return false;
	}
};

const PRIMARY_CLASS = 'primary';
const SECONDARY_CLASS = 'secondary';
const TERTIARY_CLASS = 'tertiary';

const CONTAINER = Symbol();
const SELECTION = Symbol();
const GRAPH_DB = Symbol();
const OFFSET_SIZE = Symbol();
const HIGHLIGHTS = Symbol();
const LINKS = Symbol();

export default class Links {
	constructor(graphDB, parent) {
		this[GRAPH_DB] = graphDB;
		this[HIGHLIGHTS] = [];
		this[LINKS] = [];

		this[CONTAINER] = parent.append('g')
			.attr('class', 'links');

		this[SELECTION] = this[CONTAINER]
			.selectAll('path');

		this[CONTAINER] = this[CONTAINER].node();

		setLinkOffset.call(this);
	}

	refreshData(data) {
		const minLinkSize = this.minLinkSize();

		data.forEach((link) => {
			link.width = Math.floor(link.weight * (this[GRAPH_DB].isLinkWeightNormalized ? this[OFFSET_SIZE] : 0) + minLinkSize);
		});
	}

	refreshLayout(data) {
		this[LINKS] = data;

		this[SELECTION] = this[SELECTION]
			.data(this[LINKS], (d) => d.source.id + '_' + d.target.id);

		this[SELECTION]
			.exit()
			.remove();

		this[SELECTION] = this[SELECTION]
			.enter()
			.append('path')
			.attr('id', (d) => d.source.id + '_' + d.target.id)
			.merge(this[SELECTION]);
	}

	clearHighlights() {
		this[HIGHLIGHTS] = [];
	}

	addHighlight(nodeId1, nodeId2) {
		let highlight = this[HIGHLIGHTS].find((item) => item.id === nodeId1);

		if (!highlight) {
			highlight = {
				id: nodeId1,
				links: []
			};
			this[HIGHLIGHTS].push(highlight);
		}

		highlight.links.push(nodeId2);
	}

	setStyles(focusedNode, highlightNodeType) {
		const isHighlighted = (id1, id2) => {
			const highlight = this[HIGHLIGHTS].find((item) => item.id === id1);
			return highlight ? highlight.links.includes(id2) : false;
		};

		const isHighlightedLink = (link) => {
			return (isHighlighted(link.source.id, link.target.id) || isHighlighted(link.target.id, link.source.id));
		};

		const isPrimaryLink = (link) => {
			return highlightNodeType ? false : link.source === focusedNode || link.target === focusedNode || isHighlightedLink(link);
		};

		const isSecondaryLink = (link) => {
			return highlightNodeType ? false : this[GRAPH_DB].isLinked(focusedNode, link.source) || this[GRAPH_DB].isLinked(focusedNode, link.target);
		};

		this[SELECTION]
			.attr('class', (link) => {
				let classes = 'force-link ' + (link.classes || '');

				if (focusedNode || highlightNodeType) {
					classes += ' ' + (isPrimaryLink(link) ? PRIMARY_CLASS : isSecondaryLink(link) ? SECONDARY_CLASS : TERTIARY_CLASS);
				}
				if (isHighlightedLink(link)) {
					classes += ' highlighted';
				}

				return classes;
			});
	}

	render(bounds) {
		let count = 0;
		const style = this.style();

		this[SELECTION]
			.each((link, index, elements) => {
				if (updateLine(link, elements[index], bounds, this[CONTAINER], link.style || style)) {
					count++;
				}
			});

		return count;
	}
}

Object.assign(Links.prototype, {
	maxLinkSize: method.number({
		init: 4,
		set: setLinkOffset
	}),
	minLinkSize: method.number({
		init: 1,
		set: setLinkOffset
	}),
	style: method.enum({
		init: LINK_STYLES.LINE,
		enum: LINK_STYLES
	})
});
