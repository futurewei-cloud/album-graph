import { forceLink, forceManyBody, forceSimulation, select } from 'd3';
import { uniq } from 'lodash';
import d3Helper from '../../d3Helper';
import { updateLine } from '../graphHelper';
import './LabelPlacer.less';

const SIMULATION = Symbol();
const LABEL_LAYER = Symbol();
const LABEL_NODES = Symbol();
const LABEL_LINKS = Symbol();
const SCALE = Symbol();

const last = (array) => array[array.length - 1];

const addDropShadows = (svg) => {
	const defs = svg.node().querySelector('defs') ? svg.select('defs') : svg.append('defs');

	d3Helper.dropShadow(defs, 'labelShadowDark', 0, 0, 4, 2);
	d3Helper.dropShadow(defs, 'labelShadowLight', 0, 0, 4, 2, 1, '#FFFFFF');
};

const LINK_STRENGTH = 3;
const CHARGE_FORCE_STRENGTH = -20;

export default class LabelPlacer {
	constructor(svg) {
		this[SCALE] = 1;

		addDropShadows(svg);

		this[SIMULATION] = forceSimulation()
			.force('charge_force', forceManyBody().strength(CHARGE_FORCE_STRENGTH))
			.force('links', forceLink()
				.id((d) => d.id)
				.strength(LINK_STRENGTH))
			.alphaMin(0.1)
			.stop();

		this[LABEL_LAYER] = svg.append('g')
			.attr('class', 'labels');

		this[LABEL_LINKS] = this[LABEL_LAYER].selectAll('line');
		this[LABEL_NODES] = this[LABEL_LAYER].selectAll('g');
	}

	data(data) {
		const nodes = [];
		const textNodes = [];
		const links = [];
		const isLight = document.querySelectorAll('body.light').length === 1;

		const calcShift = (bounds, offset, dist, extent, direction) => {
			let output = bounds[extent] * (offset[direction] - dist) / (dist * 2);

			return Math.max(-bounds[extent], Math.min(0, output));
		};

		const processData = () => {
			data = uniq(data);

			data.forEach((node) => {
				nodes.push({
					node: node,
					x: node.x,
					y: node.y,
					r: node.r,
					rPlus: node.rPlus
				});
				nodes.push({
					node: node,
					x: node.x,
					y: node.y,
					r: 0,
					rPlus: 0,
					isPrimary: node.isPrimary
				});
				textNodes.push(last(nodes));

				links.push({
					source: nodes[nodes.length - 2],
					target: last(nodes)
				});
			});

			if (nodes.length) {
				nodes.push({
					node: nodes[0].node,
					x: nodes[0].node.x,
					y: nodes[0].node.y,
					r: nodes[0].node.r,
					rPlus: nodes[0].node.rPlus
				});
			}

			this[SIMULATION].nodes(nodes);
			this[SIMULATION].force('links').links(links);
		};

		const preRunSimulation = () => {
			for (var i = 0; i < 30; ++i) {
				this[SIMULATION].tick();
				this[SIMULATION].nodes().forEach((node, index) => {
					if (!index % 2) {
						node.x = node.node.x;
						node.y = node.node.y;
					}
				});
				positionMouseNode();
			}
		};

		const positionMouseNode = () => {
			last(this[SIMULATION].nodes()).y += this[SCALE] * 20;
		};

		const startAnimation = () => {
			this[SIMULATION]
				.on('tick', onTick);

			this[LABEL_LINKS] = this[LABEL_LINKS]
				.data(links);

			this[LABEL_LINKS]
				.exit()
				.remove();

			this[LABEL_LINKS] = this[LABEL_LINKS]
				.enter()
				.append('line')
				.merge(this[LABEL_LINKS]);

			this[LABEL_NODES] = this[LABEL_NODES]
				.data(textNodes);

			this[LABEL_NODES]
				.exit()
				.remove();

			this[LABEL_NODES] = this[LABEL_NODES]
				.enter()
				.append('g')
				.each(function(d) {
					select(this)
						.append('text');
				})
				.merge(this[LABEL_NODES])
				.each(function(d) {
					select(this.childNodes[0])
						.text(() => d.node.label);
				})
				.attr('class', (d) => d.isPrimary ? 'primary' : '')
				.style('filter', 'url(#' + (isLight ? 'labelShadowLight' : 'labelShadowDark') + ')');
		};

		const onTick = () => {
			let offset;
			let dist;
			let shift;

			this[SIMULATION].nodes().forEach((node, index) => {
				if (index % 2) {
					if (!node.bounds) {
						node.bounds = this[LABEL_NODES].nodes()[(index - 1) / 2].childNodes[0].getBBox();
					}

					offset = {
						x: node.x - node.node.x,
						y: node.y - node.node.y
					};
					dist = Math.sqrt(offset.x * offset.x + offset.y * offset.y);

					shift = {
						x: calcShift(node.bounds, offset, dist, 'width', 'x'),
						y: calcShift(node.bounds, offset, dist, 'height', 'y') + node.bounds.height
					};

					this[LABEL_NODES].nodes()[(index - 1) / 2].childNodes[0]
						.setAttribute('transform', 'translate(' + shift.x + ',' + shift.y + ')');
				}
				else {
					node.x = node.node.x;
					node.y = node.node.y;
				}
			});
			positionMouseNode();

			this[LABEL_LINKS]
				.style('stroke-width', () => (this[SCALE] * 2) + 'px')
				.style('stroke-dasharray', (this[SCALE] * 2) + ',' + (this[SCALE] * 3))
				.each((link, index, elements) => {
					updateLine(link, elements[index], 0, this[LABEL_LAYER]);
				});

			this[LABEL_NODES]
				.attr('transform', (d) => 'translate(' + d.x + ',' + d.y + ') scale(' + this[SCALE] + ')');
		};

		this[SIMULATION].stop();
		processData();
		preRunSimulation();
		startAnimation();
	}

	scale(scale) {
		if (scale !== undefined) {
			this[SCALE] = scale;

			this[SIMULATION]
				.force('charge_force')
				.strength((d) => (d.node.r / this[SCALE]) + CHARGE_FORCE_STRENGTH * Math.pow(this[SCALE], 2));

			this.start();

			return this;
		}

		return this[SCALE];
	}

	start() {
		this[SIMULATION].alpha(0.3).restart();
	}

	remove() {
		this[LABEL_NODES].remove();
		this[LABEL_NODES] = null;

		this[LABEL_LAYER].remove();
		this[LABEL_LAYER] = null;

		this[SIMULATION].stop();
		this[SIMULATION] = null;
	}
}
