import { event, select, zoom, zoomIdentity } from 'd3';
import { isNumber, isObject, methodFunction, methodNumber, methodThickness, Thickness } from 'type-enforcer-ui';

const translate = function(x, y) {
	this[D3_ZOOM].translateBy(this[SVG], x * (1 / this[CURRENT_ZOOM].k), y * (1 / this[CURRENT_ZOOM].k));
};

const updateBounds = function() {
	this[BOUNDS].minX = -this[CURRENT_ZOOM].x / this[CURRENT_ZOOM].k;
	this[BOUNDS].minY = -this[CURRENT_ZOOM].y / this[CURRENT_ZOOM].k;

	this[BOUNDS].maxX = this[BOUNDS].minX + this[CURRENT_WIDTH] / this[CURRENT_ZOOM].k;
	this[BOUNDS].maxY = this[BOUNDS].minY + this[CURRENT_HEIGHT] / this[CURRENT_ZOOM].k;
};

const SVG = Symbol();
const ZOOM_LAYER = Symbol();
const D3_ZOOM = Symbol();
const CURRENT_ZOOM = Symbol();
const BOUNDS = Symbol();
const CURRENT_WIDTH = Symbol();
const CURRENT_HEIGHT = Symbol();

export default class Layout {
	constructor(container) {
		this[SVG] = select(container).append('svg:svg');
		this[ZOOM_LAYER] = this[SVG].append('g');
		this[BOUNDS] = {
			minX: 0,
			minY: 0,
			maxX: 0,
			maxY: 0
		};
		this[CURRENT_ZOOM] = {
			k: 1,
			x: 0,
			y: 0
		};
		this[CURRENT_WIDTH] = 0;
		this[CURRENT_HEIGHT] = 0;

		this[D3_ZOOM] = zoom()
			.on('zoom', () => {
				this[CURRENT_ZOOM] = event.transform;
				this[ZOOM_LAYER].attr('transform', this[CURRENT_ZOOM]);
				updateBounds.call(this);
				if (this.onZoom()) {
					this.onZoom()(this[CURRENT_ZOOM].k);
				}
			});

		this[D3_ZOOM](this[SVG]);
	}

	bounds() {
		return this[BOUNDS];
	}

	container() {
		return this[ZOOM_LAYER];
	}

	zoom(args) {
		const padding = this.padding();
		const offsetX = (padding.left - padding.right) / 2;
		const offsetY = (padding.top - padding.bottom) / 2;

		const zoomToBox = (range) => {
			const scaleX = (this[CURRENT_WIDTH] - padding.horizontal) / (range.max.x - range.min.x);
			const scaleY = (this[CURRENT_HEIGHT] - padding.vertical) / (range.max.y - range.min.y);
			let scale = Math.min(scaleX, scaleY);
			let newX = ((range.max.x + range.min.x) / 2) * scale;
			let newY = ((range.max.y + range.min.y) / 2) * scale;
			newX -= (padding.left - padding.right) / 2;
			newY -= (padding.top - padding.bottom) / 2;

			animate((this[CURRENT_WIDTH] / 2) - newX, (this[CURRENT_HEIGHT] / 2) - newY, scale);
		};

		const scaleAroundPoint = (x, y, scale) => {
			const diff = 1 - (scale / this[CURRENT_ZOOM].k);
			const diffX = (x - this[CURRENT_ZOOM].x) * diff;
			const diffY = (y - this[CURRENT_ZOOM].y) * diff;

			animate(this[CURRENT_ZOOM].x + diffX, this[CURRENT_ZOOM].y + diffY, scale);
		};

		const scaleToPoint = (x, y, scale) => {
			animate((this[CURRENT_WIDTH] / 2) - x * scale, (this[CURRENT_HEIGHT] / 2) - y * scale, scale);
		};

		const animate = (x, y, scale) => {
			this[SVG].transition()
				.duration(500)
				.call(this[D3_ZOOM].transform, zoomIdentity
					.translate(x, y)
					.scale(scale));
		};

		if (args !== undefined) {
			if (isObject(args)) {
				if (args.min.x === args.max.x && args.min.y === args.max.y) {
					scaleToPoint(args.min.x - offsetX, args.min.y - offsetY, 1);
				}
				else {
					zoomToBox(args);
				}
			}
			else if (args === 'center') {
				scaleToPoint(offsetX, offsetY, this[CURRENT_ZOOM].k);
			}
			else if (isNumber(args)) {
				scaleAroundPoint(((this[CURRENT_WIDTH] / 2) + offsetX), ((this[CURRENT_HEIGHT] / 2) + offsetY), args);
			}

			return this;
		}

		return this[CURRENT_ZOOM].k;
	}
}

Object.assign(Layout.prototype, {
	onZoom: methodFunction(),
	width: methodNumber({
		set(width) {
			translate.call(this, (width - this[CURRENT_WIDTH]) / 2, 0);
			this[CURRENT_WIDTH] = width;
			this[SVG].style('width', width + 'px');
			updateBounds.call(this);
		}
	}),
	height: methodNumber({
		set(height) {
			translate.call(this, 0, (height - this[CURRENT_HEIGHT]) / 2);
			this[CURRENT_HEIGHT] = height;
			this[SVG].style('height', height + 'px');
			updateBounds.call(this);
		}
	}),
	padding: methodThickness({
		init: new Thickness('20px')
	})
});
