import { forOwn } from 'object-agent';
import { applySettings, methodFunction, methodString } from 'type-enforcer-ui';
import './ForceGraph.less';
import GraphDB from './GraphDB';
import Layout from './Layout';
import Links from './links/Links';
import Nodes from './nodes/Nodes';
import Simulation from './Simulation';

export { LINK_WEIGHT_TYPES, NODE_WEIGHT_TYPES } from './GraphDB';

const mergeStats = (stats, field, graphStats) => {
	stats.nodes.all[field] = 0;
	forOwn(graphStats, (value, type) => {
		if (!stats.nodes[type]) {
			stats.nodes[type] = {};
		}
		stats.nodes[type][field] = value;
		stats.nodes.all[field] += value;
	});
};

const randomStart = () => {
	let x = Math.random() - 0.5;
	x += x > 0 ? 0.5 : -0.5;
	return x * 1000;
};

const GRAPH_DB = Symbol();
const LAYOUT = Symbol();
const SIMULATION = Symbol();
const NODES = Symbol();
const LINKS = Symbol();
const STATS = Symbol();

export default class ForceGraph {
	constructor(settings) {
		const self = this;
		self[GRAPH_DB] = new GraphDB();
		self[LAYOUT] = new Layout(settings.container)
			.onZoom((k) => {
				self[SIMULATION].bump();
				self[NODES].zoom(k);
			});
		self[SIMULATION] = new Simulation(self[GRAPH_DB])
			.onTick(() => {
				const count = self[NODES].render(self[LAYOUT].bounds());
				forOwn(self[STATS].nodes, (value, key) => {
					value.rendered = count[key] ? count[key].rendered : 0;
				});

				self[STATS].links.all.rendered = self[LINKS].render(self[LAYOUT].bounds());

				if (self.onRender() && self[STATS].nodes.all.total) {
					self.onRender()(self[STATS]);
				}
			});
		self[LINKS] = new Links(self[GRAPH_DB], self[LAYOUT].container());
		self[NODES] = new Nodes(self[GRAPH_DB], self[LAYOUT].container(), self[SIMULATION], self[LINKS]);
		self[STATS] = {
			nodes: {
				all: {
					total: 0,
					filtered: 0,
					rendered: 0,
					detached: 0
				}
			},
			links: {
				all: {
					total: 0,
					filtered: 0,
					rendered: 0
				}
			}
		};

		self[GRAPH_DB]
			.onProcessNode((node, oldNode) => {
				if (self.onProcessNode()) {
					self.onProcessNode()(node);
				}
				forOwn(oldNode, (value, key) => {
					if (key !== 'meta') {
						node[key] = value;
					}
				});
				if (node.x === undefined) {
					node.x = randomStart();
					node.y = randomStart();
				}
				node.classes = node.classes || '';
			})
			.onProcessLink((link) => {
				if (self.onProcessLink()) {
					self.onProcessLink()(link);
				}
				if (link.source.id) {
					link.source = link.source.id;
				}
				if (link.target.id) {
					link.target = link.target.id;
				}
			})
			.onFilter((data) => {
				self[SIMULATION].pause();
				self[STATS].links.all.filtered = data.edges.length;
				mergeStats(self[STATS], 'detached', self[GRAPH_DB].stats.detachedNodes);
				mergeStats(self[STATS], 'filtered', self[GRAPH_DB].stats.filteredNodes);
				self.refresh();
			});

		applySettings(self, settings);
	}

	data(data) {
		const self = this;

		return new Promise((resolve) => {
			self[GRAPH_DB].data(data)
				.then(() => {
					forOwn(self[GRAPH_DB].nodeTypes, (value, type) => {
						self[STATS].nodes[type] = {
							total: value,
							filtered: value,
							rendered: 0,
							detached: 0
						};
					});
					self[STATS].nodes.all.total = self[GRAPH_DB].totalNodes;
					self[STATS].links.all.total = self[GRAPH_DB].totalEdges;
					resolve();
				});

		});
	}

	filter() {
		return this[GRAPH_DB].filter();
	}

	onSelectionChange(onChange) {
		return this[NODES].onSelectionChange(onChange);
	}

	normalizeWeights(normalizeWeights) {
		return this[GRAPH_DB].normalizeWeights(normalizeWeights);
	}

	width(width) {
		return this[LAYOUT].width(width);
	}

	height(height) {
		return this[LAYOUT].height(height);
	}

	hiddenNodeTypes(types) {
		return this[GRAPH_DB].hiddenNodeTypes(types);
	}

	filterFunc(filterFunc) {
		return this[GRAPH_DB].filterFunc(filterFunc);
	}

	calcNodeWeightBy(calcNodeWeightBy) {
		return this[GRAPH_DB].calcNodeWeightBy(calcNodeWeightBy);
	}

	calcLinkWeightBy(calcLinkWeightBy) {
		return this[GRAPH_DB].calcLinkWeightBy(calcLinkWeightBy);
	}

	nodeCharge(charge) {
		return this[SIMULATION].nodeCharge(charge);
	}

	linkStrength(strength) {
		return this[SIMULATION].linkStrength(strength);
	}

	xStrength(strength) {
		return this[SIMULATION].xStrength(strength);
	}

	yStrength(strength) {
		return this[SIMULATION].yStrength(strength);
	}

	showShortestPaths(show) {
		return this[NODES].showShortestPaths(show);
	}

	labelExtent(extent) {
		return this[NODES].labelExtent(extent);
	}

	labelExtentOnMouseOver(extent) {
		return this[NODES].labelExtentOnMouseOver(extent);
	}

	showLabelsOnNodes(show) {
		return this[NODES].showLabelsOnNodes(show);
	}

	hideDetachedNodes(hide) {
		return this[GRAPH_DB].hideDetachedNodes(hide);
	}

	maxLinkSize(size) {
		return this[LINKS].maxLinkSize(size);
	}

	minLinkSize(size) {
		return this[LINKS].minLinkSize(size);
	}

	linkStyle(style) {
		return this[LINKS].style(style);
	}

	maxNodeRadius(size) {
		return this[NODES].maxNodeRadius(size);
	}

	minNodeRadius(size) {
		return this[NODES].minNodeRadius(size);
	}

	clipNodes(size) {
		return this[NODES].clip(size);
	}

	selectedNodeZoom(size) {
		return this[NODES].selectedNodeZoom(size);
	}

	onNodeClick(callback) {
		return this[NODES].onClick(callback);
	}

	singleSelect(select) {
		return this[NODES].singleSelect(select);
	}

	zoom(...args) {
		if (args.length) {
			if (args[0] === 'fit') {
				args[0] = this[NODES].bounds();
			}
			else if (args[0] === 'selected') {
				args[0] = this[NODES].bounds(true);
			}
			else if (args[0] === 'id') {
				args[0] = this[NODES].bounds(args[1]);
			}

			this[LAYOUT].zoom(args[0]);

			return this;
		}

		return this[NODES].zoom();
	}

	padding(padding) {
		return this[LAYOUT].padding(padding);
	}

	select(node) {
		this[NODES].select(node);
		this.refresh();
	}

	refresh() {
		const data = this[GRAPH_DB].data();
		this[NODES].refreshData(data.nodes);
		this[LINKS].refreshData(data.edges);
		this[SIMULATION].refresh(data);
		this[NODES].refreshLayout(this[SIMULATION].nodes());
		this[LINKS].refreshLayout(this[SIMULATION].links());
	}
}

Object.assign(ForceGraph.prototype, {
	onRender: methodFunction(),
	onProcessNode: methodFunction(),
	onProcessLink: methodFunction(),
	highlightNodeType: methodString({
		set(highlightNodeType) {
			return this[NODES].setStyles(highlightNodeType);
		}
	})
});
