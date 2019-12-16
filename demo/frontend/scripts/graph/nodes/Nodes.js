import { drag, event, select } from 'd3';
import { uniq } from 'lodash';
import { clone, combo } from 'object-agent';
import { method } from 'type-enforcer-ui';
import LabelPlacer from './LabelPlacer';
import './Nodes.less';

const CIRCLE_CLIP_ID = 'circleClip';
const CIRCLE_CLIP_URL = 'url(#' + CIRCLE_CLIP_ID + ')';

const getImageDimensions = function(g, node) {
	const self = this;
	let tempImage = new Image();
	tempImage.onload = () => {
		const currentNode = self[SELECTION].data().find((item) => item.id === node.id);
		if (currentNode) {
			currentNode.imageWidth = tempImage.width;
			currentNode.imageHeight = tempImage.height;
			setImageSize(g, currentNode);
		}
		tempImage = null;
	};
	tempImage.src = g.select('image').attr('xlink:href');
};

const getImageRenderSize = (node, plus) => {
	let extra = plus ? (node.rPlus - node.r) * 2 : 0;
	let width = node.r * 2;
	let height = width;

	if (node.imageWidth && !node.clip) {
		const ratio = node.imageWidth / node.imageHeight;

		if (ratio > 1) {
			height *= (1 / ratio);
		}
		else {
			width *= (1 / ratio);
		}
	}

	return {
		height: height + extra,
		width: width + extra
	};
};

const setImageSize = (g, node) => {
	const {height, width} = getImageRenderSize(node);

	g.select('rect')
		.attr('x', -width / 2)
		.attr('y', -height / 2)
		.attr('width', width)
		.attr('height', height);
	g.select('image')
		.attr('x', -width / 2)
		.attr('y', -height / 2)
		.attr('width', width)
		.attr('height', height);
};

const setNodeSizeOffset = function() {
	this[OFFSET_RADIUS] = this.maxNodeRadius() - this.minNodeRadius();
};

const setDragEvents = function() {
	if (!this[DRAG_HANDLER]) {
		this[DRAG_HANDLER] = drag()
			.on('start', (d) => {
				this[IS_DRAGGING] = true;
				if (!event.active) {
					this[SIMULATION].startPerpetual();
				}
				d.fx = d.x;
				d.fy = d.y;
			})
			.on('drag', (d) => {
				d.fx = event.x;
				d.fy = event.y;
			})
			.on('end', (d) => {
				this[IS_DRAGGING] = false;
				if (!event.active) {
					this[SIMULATION].stopPerpetual();
				}
				if (!d.isSelected) {
					d.fx = null;
					d.fy = null;
				}
			});
	}

	this[DRAG_HANDLER](this[SELECTION]);
};

const onMouseEnterNode = function(node) {
	if (!this[FOCUSED_NODE] && !this[IS_DRAGGING]) {
		this[FOCUSED_NODE] = node;
		this[FOCUSED_NODE].isPrimary = true;

		lock(this[FOCUSED_NODE]);

		if (this[FOCUSED_NODE].tooltip) {
			this[TOOLTIP] = select('body')
				.append('div')
				.attr('class', 'tooltip')
				.style('left', event.clientX + 14 + 'px')
				.style('top', event.clientY - 14 + 'px')
				.html(this[FOCUSED_NODE].tooltip);
		}

		highlightPaths.call(this);
	}
};

const onMouseLeaveNode = function() {
	if (this[FOCUSED_NODE] && !this[IS_DRAGGING]) {
		if (!this[FOCUSED_NODE].isSelected) {
			unlock(this[FOCUSED_NODE]);
		}
		this[FOCUSED_NODE].isPrimary = false;

		if (this[TOOLTIP]) {
			this[TOOLTIP].remove();
			this[TOOLTIP] = null;
		}

		this[FOCUSED_NODE] = null;
		highlightPaths.call(this);
	}
};

const onClickNode = function() {
	if (this[FOCUSED_NODE]) {
		this.select(this[FOCUSED_NODE]);
		if (this.onClick()) {
			this.onClick()(this[FOCUSED_NODE]);
		}
	}
};

const highlightPaths = function(buildSelected = false) {
	const promises = [];

	const getPaths = (node1, node2, array) => new Promise((resolve) => {
		this[GRAPH_DB].shortestPaths(node1, node2)
			.then((paths) => {
				paths.forEach((path) => array.push(path));
				resolve();
			});
	});

	this[HIGHLIGHTED_PATHS].length = 0;

	if (this.showShortestPaths()) {
		if (buildSelected) {
			this[SELECTED_PATHS].length = 0;

			combo(this[SELECTED]).forEach(([node1, node2]) => {
				promises.push(getPaths(node1, node2, this[SELECTED_PATHS]));
			});
		}
		else if (this[FOCUSED_NODE] && !this[FOCUSED_NODE].isSelected) {
			this[SELECTED].forEach((selectedNode) => {
				promises.push(getPaths(this[FOCUSED_NODE], selectedNode, this[HIGHLIGHTED_PATHS]));
			});
		}
	}

	this.setStyles();
	setLabelScale.call(this);

	Promise.all(promises)
		.then(() => {
			this[SELECTED_PATHS].forEach((path) => {
				this[HIGHLIGHTED_PATHS].push(path);
			});

			this[HIGHLIGHTED_NODES] = [];

			this[HIGHLIGHTED_PATHS].forEach((path) => {
				path.forEach((node) => {
					this[HIGHLIGHTED_NODES].push(node);
				});
			});

			refreshHighlighted.call(this);

			this[LINKS].clearHighlights();
			this[HIGHLIGHTED_PATHS].forEach((path) => {
				path.some((node, index) => {
					if (index < path.length - 1) {
						this[LINKS].addHighlight(node.id, path[index + 1].id);
					}
				});
			});

			this.setStyles();
			setLabelScale.call(this);
		});
};

const refreshHighlighted = function() {
	const clip = this.clip();

	this[HIGHLIGHT_SELECTION] = this[HIGHLIGHT_SELECTION]
		.data(this[HIGHLIGHTED_NODES]
			.map((highlightedNode) => ({node: highlightedNode})), (d) => d.node.id);

	this[HIGHLIGHT_SELECTION]
		.exit()
		.remove();

	this[HIGHLIGHT_SELECTION] = this[HIGHLIGHT_SELECTION]
		.enter()
		.append('g')
		.attr('class', 'highlighted-node')
		.each(function(d) {
			const g = select(this);

			if (!d.node.image || clip || d.node.clip) {
				g.append('circle');
			}
			else {
				g.append('rect')
					.attr('rx', '4')
					.attr('ry', '4');
			}
		})
		.merge(this[HIGHLIGHT_SELECTION])
		.each(function(d) {
			const g = select(this);
			const thisClip = clip || d.node.clip;

			if (!d.node.image || thisClip) {
				g.select('circle')
					.attr('r', d.node.rPlus);
			}
			else {
				const {height, width} = getImageRenderSize(d.node, true);

				g.select('rect')
					.attr('x', -width / 2)
					.attr('y', -height / 2)
					.attr('width', width)
					.attr('height', height);
			}
		});

	this[SIMULATION].bump();
};

const setLabelScale = function() {
	if (this[LABEL_PLACER]) {
		this[LABEL_PLACER].scale(1 / this.zoom());
	}
};

const lock = (node) => {
	node.fx = node.x || 0;
	node.fy = node.y || 0;
};

const unlock = (node) => {
	node.fx = null;
	node.fy = null;
};

const updateNodeSelected = function(node) {
	node.isSelected = true;
	node.extraCharge = ((node.selectedNodeZoom || this.selectedNodeZoom()) / 8) + 1;
	lock(node);
	updateNodePost.call(this, node);

	return node;
};

const updateNodeNotSelected = function(node) {
	node.isSelected = false;
	node.extraCharge = null;
	unlock(node);
	updateNodePost.call(this, node);

	return node;
};

const updateNodePost = function(node) {
	setNodeRadius.call(this, node);

	this[SELECTION].each(function(d) {
		if (d.id === node.id) {
			setImageSize(select(this), node);
		}
	});
};

const setNodeRadius = function(node) {
	node.r = (node.weight * this[OFFSET_RADIUS] + this.minNodeRadius()) * (node.isSelected ? (node.selectedNodeZoom || this.selectedNodeZoom()) : 1);
	node.rPlus = node.r + NODE_MARGIN;
};

const PRIMARY_CLASS = 'primary';
const SECONDARY_CLASS = 'secondary';
const TERTIARY_CLASS = 'tertiary';

const NODE_MARGIN = 8;

const PARENT = Symbol();
const CONTAINER = Symbol();
const SELECTION = Symbol();
const HIGHLIGHT_CONTAINER = Symbol();
const HIGHLIGHT_SELECTION = Symbol();
const GRAPH_DB = Symbol();
const SIMULATION = Symbol();
const LINKS = Symbol();
const OFFSET_RADIUS = Symbol();
const HIGHLIGHTED_NODES = Symbol();
const SELECTED = Symbol();
const DRAG_HANDLER = Symbol();
const IS_DRAGGING = Symbol();
const FOCUSED_NODE = Symbol();
const TOOLTIP = Symbol();
const SELECTED_PATHS = Symbol();
const HIGHLIGHTED_PATHS = Symbol();
const LABEL_PLACER = Symbol();

export default class Nodes {
	constructor(graphDB, parent, simulation, links) {
		this[PARENT] = parent;
		this[GRAPH_DB] = graphDB;
		this[SIMULATION] = simulation;
		this[LINKS] = links;
		this[HIGHLIGHTED_NODES] = [];
		this[SELECTED] = [];
		this[SELECTED_PATHS] = [];
		this[HIGHLIGHTED_PATHS] = [];

		this[CONTAINER] = parent.append('g')
			.attr('class', 'nodes');

		this[CONTAINER].append('defs')
			.append('clipPath')
			.attr('id', CIRCLE_CLIP_ID)
			.attr('clipPathUnits', 'objectBoundingBox')
			.append('circle')
			.attr('cx', '0.5')
			.attr('cy', '0.5')
			.attr('r', '0.5');

		this[SELECTION] = this[CONTAINER]
			.selectAll('g');

		this[HIGHLIGHT_CONTAINER] = parent.append('g')
			.attr('class', 'highlighted-nodes');

		this[HIGHLIGHT_SELECTION] = this[HIGHLIGHT_CONTAINER]
			.selectAll('circle');

		setNodeSizeOffset.call(this);
	}

	refreshData(data) {
		const self = this;
		data.forEach((node) => {
			setNodeRadius.call(self, node);
			if (node.isSelected === true) {
				updateNodeSelected.call(self, node);
			}
		});
	}

	refreshLayout(data) {
		const self = this;
		const clip = self.clip();

		this[SELECTION] = this[SELECTION]
			.data(data, (d) => d.id);

		this[SELECTION]
			.exit()
			.remove();

		this[SELECTION] = this[SELECTION]
			.enter()
			.append('g')
			.each(function(d) {
				const g = select(this);

				if (!d.image) {
					g.append('circle');
					if (d.icon) {
						g.append('text')
							.classed('node-icon', true);
					}
					if (self.showLabelsOnNodes()) {
						g.append('text')
							.classed('node-label', true);
					}
				}
				else {
					g.append('rect')
						.attr('rx', '2')
						.attr('ry', '2');
					g.append('image')
						.on('load', () => {
							getImageDimensions.call(self, select(this), d);
						});
				}
			})
			.on('mouseenter.fade', (node) => {
				onMouseEnterNode.call(self, node);
			})
			.on('mouseleave.fade', () => {
				onMouseLeaveNode.call(self);
			})
			.on('click', () => {
				onClickNode.call(self);
			})
			.merge(this[SELECTION])
			.each(function(d) {
				const g = select(this);

				if (!d.image) {
					g.select('circle')
						.attr('r', d.r);

					if (d.icon) {
						g.select('.node-icon')
							.text(d.icon);
					}
					if (self.showLabelsOnNodes()) {
						g.select('.node-label')
							.text(d.label);
					}
				}
				else {
					const thisClip = clip || d.clip;

					g.select('rect')
						.style('opacity', d.isSelected ? 1 : 0);
					g.select('image')
						.attr('preserveAspectRatio', thisClip ? 'xMidYMid slice' : null)
						.attr('clip-path', thisClip ? CIRCLE_CLIP_URL : null)
						.attr('xlink:href', d.isSelected ? d.image.medium : d.image.small);
				}

				setImageSize(g, d);
			});

		this.refreshSelected();

		setDragEvents.call(this);
		highlightPaths.call(this, true);
	}

	refreshSelected() {
		this[SELECTED] = this[SELECTED]
			.map((selectedNode) => this[GRAPH_DB].node(selectedNode.id))
			.filter(Boolean);

		this[SELECTION].each((node) => {
			if (node.isSelected) {
				this[SELECTED].push(updateNodeSelected.call(this, node));
			}
		});
		this[SELECTED] = uniq(this[SELECTED]);

		this[SELECTED].forEach((selectedNode) => {
			selectedNode.classes = (selectedNode.classes || '') + ' selected';
		});

		if (this.onSelectionChange()) {
			this.onSelectionChange()(clone(this[SELECTED]));
		}
	}

	setStyles(highlightNodeType) {
		const self = this;

		const isPrimaryNode = (node) => {
			if (highlightNodeType) {
				if (highlightNodeType === 'selected') {
					return node.isSelected;
				}
				return node.type === highlightNodeType;
			}
			return self[GRAPH_DB].isLinked(self[FOCUSED_NODE], node) || self[HIGHLIGHTED_NODES].includes(node);
		};

		const isSecondaryNode = (node) => {
			if (highlightNodeType) {
				return false;
			}
			return self[GRAPH_DB].isLinked(self[FOCUSED_NODE], node, 2);
		};

		self[SELECTION]
			.attr('class', (node) => {
				let classes = 'force-node ' + (node.classes || '');

				if (self[FOCUSED_NODE] || highlightNodeType) {
					classes += ' ' + (isPrimaryNode(node) ? PRIMARY_CLASS : isSecondaryNode(node) ? SECONDARY_CLASS : TERTIARY_CLASS);
				}
				if (node.isSelected) {
					classes += ' selected';
				}

				return classes;
			});

		self[LINKS].setStyles(self[FOCUSED_NODE], highlightNodeType);
		self.showLabels();
	}

	render(bounds) {
		let count = {};

		const add = (type) => {
			if (!count[type]) {
				count[type] = {
					rendered: 0
				};
			}
			count[type].rendered++;
		};

		this[SELECTION]
			.style('transform', (d) => 'translate(' + d.x + 'px,' + d.y + 'px)')
			.style('display', (node) => {
				let output = 'none';

				if (!(node.x + node.r < bounds.minX || node.x - node.r > bounds.maxX || node.y + node.r < bounds.minY || node.y - node.r > bounds.maxY)) {
					add('all');
					add(node.type);
					output = null;
				}

				return output;
			});

		this[HIGHLIGHT_SELECTION]
			.style('transform', (d) => 'translate(' + d.node.x + 'px,' + d.node.y + 'px)')
			.style('display', (node) => {
				let output = 'none';

				node = node.node;

				if (!(node.x + node.r < bounds.minX || node.x - node.r > bounds.maxX || node.y + node.r < bounds.minY || node.y - node.r > bounds.maxY)) {
					output = null;
				}

				return output;
			});

		if (this[LABEL_PLACER]) {
			this[LABEL_PLACER].start();
		}

		return count;
	}

	select(node) {
		node = this[GRAPH_DB].node(node.id || node);
		node.isSelected = !node.isSelected;

		if (!node.isSelected) {
			if (!this.singleSelect()) {
				this[SELECTED] = this[SELECTED].filter((item) => item !== node);
				updateNodeNotSelected.call(this, node);
			}
		}
		else {
			if (this.singleSelect()) {
				updateNodeNotSelected.call(this, this[SELECTED].shift());
			}
			this[SELECTED].push(updateNodeSelected.call(this, node));
		}

		if (!this[SELECTED].length && this.highlightNodeType() === 'selected') {
			this.highlightNodeType('');
		}

		if (this.onSelectionChange()) {
			this.onSelectionChange()(clone(this[SELECTED]));
		}

		this[SIMULATION].refresh();
		highlightPaths.call(this);
	}

	showLabels() {
		let labelNodes = [];
		let highlightedLabelNodes = [];

		const merge = (array1, array2, extent = 0) => {
			array2.forEach((node) => {
				if (node && !array1.includes(node)) {
					if (node.label) {
						array1.push(node);
					}
					if (extent > 1 && this[GRAPH_DB].hasLinks(node)) {
						merge(array1, this[GRAPH_DB].linkedNodes(node), extent - 1);
					}
				}
			});
		};

		if ((this[FOCUSED_NODE] || this[SELECTED].length) && (this.labelExtent() || this.labelExtentOnMouseOver())) {
			if (!this[LABEL_PLACER]) {
				this[LABEL_PLACER] = new LabelPlacer(this[PARENT]);
			}

			merge(labelNodes, this[SELECTED], this.labelExtent());
			merge(highlightedLabelNodes, this[HIGHLIGHTED_NODES]);

			if (highlightedLabelNodes.length + labelNodes.length < 50) {
				merge(labelNodes, highlightedLabelNodes);
			}

			merge(labelNodes, [this[FOCUSED_NODE]], this.labelExtentOnMouseOver());
		}

		if (labelNodes.length) {
			this[LABEL_PLACER].data(labelNodes);
		}
		else if (this[LABEL_PLACER]) {
			this[LABEL_PLACER].remove();
			this[LABEL_PLACER] = null;
		}
	}

	bounds(isSelected) {
		const findLimits = (callback) => {
			let isInit = false;
			let range = {
				min: {
					x: 0,
					y: 0
				},
				max: {
					x: 0,
					y: 0
				}
			};

			this[SELECTION].each((d) => {
				if (callback(d)) {
					if (!isInit) {
						range.min.x = d.x - d.r;
						range.min.y = d.y - d.r;
						range.max.x = d.x + d.r;
						range.max.y = d.y + d.r;
						isInit = true;
					}
					else {
						range.min.x = Math.min(range.min.x, d.x - d.r);
						range.min.y = Math.min(range.min.y, d.y - d.r);
						range.max.x = Math.max(range.max.x, d.x + d.r);
						range.max.y = Math.max(range.max.y, d.y + d.r);
					}
				}
			});

			return range;
		};

		const nodePosition = (node) => {
			return {
				min: {
					x: node.x,
					y: node.y
				},
				max: {
					x: node.x,
					y: node.y
				}
			};
		};

		if (isSelected === true) {
			if (this[SELECTED].length > 1) {
				return findLimits((d) => this[HIGHLIGHTED_NODES].includes(d));
			}
			else if (this[SELECTED].length === 1) {
				return nodePosition(this[SELECTED][0]);
			}
		}

		if (isSelected) {
			const node = this[SELECTION].data().find((node) => {
				return node.id === isSelected;
			});

			if (node) {
				return nodePosition(node);
			}
		}

		return findLimits(() => true);
	}
}

Object.assign(Nodes.prototype, {
	maxNodeRadius: method.number({
		init: 15,
		set: setNodeSizeOffset
	}),
	minNodeRadius: method.number({
		init: 4,
		set: setNodeSizeOffset
	}),
	selectedNodeZoom: method.number({
		init: 1
	}),
	showShortestPaths: method.boolean({
		init: true
	}),
	labelExtent: method.integer({
		init: 1
	}),
	labelExtentOnMouseOver: method.integer({
		init: 2
	}),
	showLabelsOnNodes: method.boolean(),
	onSelectionChange: method.function(),
	zoom: method.number({
		set: setLabelScale
	}),
	clip: method.boolean(),
	onClick: method.function(),
	singleSelect: method.boolean()
});
