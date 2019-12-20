import { List } from 'hord';
import { debounce } from 'lodash';
import { combo, forOwn } from 'object-agent';
import { Enum, methodArray, methodBoolean, methodEnum, methodFunction } from 'type-enforcer-ui';
import WeightNormalizer from './WeightNormalizer';

const processData = (options) => new Promise((resolve) => {
	const weights = new WeightNormalizer();
	let oldItem;

	options.data.forEach((item) => {
		if (options.getItem) {
			oldItem = options.getItem(item);
		}
		if (options.processCallback) {
			options.processCallback(item, oldItem);
		}

		const weight = options.eachBefore(item);

		if (options.normalizeWeights && weight !== undefined) {
			weights.add(weight);
		}
	});

	if (options.between) {
		options.between();
	}

	if (options.normalizeWeights) {
		weights.done();

		options.data.forEach((item) => {
			item.weight = weights.calc(item.weight);
		});
	}

	resolve();
});

const setNode = function(node, isFull) {
	this[isFull ? FULL_NODE_INDEX : NODE_INDEX].push(node);
};

const getNode = function(nodeId, isFull) {
	return this[isFull ? FULL_NODE_INDEX : NODE_INDEX].find((node) => node.id === nodeId);
};

const getLink = function(nodeId, isFull) {
	return this[isFull ? FULL_LINK_INDEX : LINK_INDEX].find((link) => link.id === nodeId);
};

const setLink = function(link, isFull) {
	const index = this[isFull ? FULL_LINK_INDEX : LINK_INDEX];

	const addNode = (node1, node2, direction) => {
		let node = index.find((link) => link.id === node1);

		if (!node) {
			node = {
				id: node1,
				to: [],
				from: [],
				all: []
			};
			index.push(node);
		}

		if (!node[direction].includes(node2)) {
			node[direction].push(node2);
		}
		if (!node.all.includes(node2)) {
			node.all.push(node2);
		}
	};

	addNode(link.source.id, link.target.id, 'from');
	addNode(link.target.id, link.source.id, 'to');
};

const resetStats = function(field) {
	if (!this[STATS][field]) {
		this[STATS][field] = {};
	}
	forOwn(this.nodeTypes, (value, type) => {
		this[STATS][field][type] = 0;
	});
};

const filter = debounce(function() {
	const self = this;

	const cloneData = () => new Promise((resolve) => {
		const data = self[PROCESSED_DATA];

		self[LINK_INDEX].values([]);

		data.nodes.forEach((node) => {
			setNode.call(self, node);
		});

		resolve(data);
	});

	const removeHiddenNodes = (data) => new Promise((resolve) => {
		const linkableNodes = [];
		const newLinks = [];
		const oldNodes = {};
		let mergedLinks = 0;
		const hiddenNodeTypes = self.hiddenNodeTypes();
		const filterFunc = self.filterFunc();

		const saveNewLinks = (linkableNodes, mergedLinks) => {
			combo(linkableNodes).forEach(([node1, node2]) => {
				const match = newLinks.find((link) => {
					return (link.source === node1 && link.target === node2) || (link.source === node2 && link.target === node1);
				});

				if (match) {
					match.mergedLinks += mergedLinks;
				}
				else {
					newLinks.push({
						source: node1,
						target: node2,
						weight: 1,
						mergedLinks: mergedLinks
					});
				}
			});
		};

		const checkNode = (node, level = 1) => {
			if (hiddenNodeTypes.includes(node.type)) {
				if (!oldNodes[node.id]) {
					if (level === 1) {
						mergedLinks = 0;
						linkableNodes.length = 0;
					}

					mergedLinks++;
					oldNodes[node.id] = true;

					const nodeIndexEntry = getLink.call(self, node.id, true);
					if (nodeIndexEntry) {
						nodeIndexEntry.all.forEach((id) => {
							checkNode(getNode.call(this, id), level + 1);
						});
					}

					if (level === 1) {
						saveNewLinks(linkableNodes, mergedLinks);
					}
				}
			}
			else if (!linkableNodes.includes(node)) {
				linkableNodes.push(node);
			}
		};

		if (hiddenNodeTypes.length || filterFunc !== undefined) {
			data.nodes.forEach((node) => {
				checkNode(node);
			});

			data.edges = data.edges.filter((edge) => !(hiddenNodeTypes.includes(edge.source.type) ||
				hiddenNodeTypes.includes(edge.target.type)));
			data.nodes = data.nodes.filter((node) => !hiddenNodeTypes.includes(node.type));

			if (filterFunc !== undefined) {
				data.nodes = data.nodes.filter((node) => {
					const keep = filterFunc(node);

					if (!keep) {
						data.edges = data.edges.filter((edge) => !(edge.source.id === node.id || edge.target.id === node.id));
					}

					return keep;
				});
			}

			newLinks.forEach((link) => {
				if (!this.isLinked(link.source, link.target)) {
					data.edges.push(link);
					setLink.call(self, link);
				}
			});
		}

		data.edges.forEach((link) => {
			if (!this.isLinked(link.source, link.target)) {
				setLink.call(self, link);
			}
		});

		resolve(data);
	});

	const hideDetachedNodes = (data) => new Promise((resolve) => {
		const hideDetached = self.hideDetachedNodes();

		resetStats.call(this, 'detachedNodes');
		resetStats.call(this, 'filteredNodes');

		data.nodes.forEach((node) => {
			const isDetached = !self.hasLinks(node);

			if (isDetached) {
				self[STATS].detachedNodes[node.type]++;
			}
			if (!(hideDetached && isDetached)) {
				self[STATS].filteredNodes[node.type]++;
			}
		});

		if (hideDetached) {
			data.nodes = data.nodes.filter((node) => self.linkedNodes(node).length);
		}

		resolve(data);
	});

	const calcWeights = (data) => new Promise((resolve) => {
		const weights = new WeightNormalizer();

		if (self.calcNodeWeightBy() === NODE_WEIGHT_TYPES.DONE) {
			this[IS_NODE_WEIGHT_NORMALIZED] = true;
		}
		else if (self.calcNodeWeightBy() === NODE_WEIGHT_TYPES.QUANT_LINKS) {
			this[IS_NODE_WEIGHT_NORMALIZED] = weights.normalize(data.nodes, (node) => self.linkedNodes(node).length);
		}

		if (self.calcLinkWeightBy() === LINK_WEIGHT_TYPES.DONE) {
			this[IS_LINK_WEIGHT_NORMALIZED] = true;
		}
		else if (self.calcLinkWeightBy() === LINK_WEIGHT_TYPES.QUANT_MERGED) {
			this[IS_LINK_WEIGHT_NORMALIZED] = weights.normalize(data.edges, (edge) => edge.mergedLinks || 0);
		}

		resolve(data);
	});

	const finalize = (data) => new Promise((resolve) => {
		self[FILTERED_DATA] = data;

		if (self.onFilter()) {
			self.onFilter()(self[FILTERED_DATA]);
		}
		resolve();
	});

	return new Promise((resolve) => {
		if (self[PROCESSED_DATA]) {
			cloneData()
				.then(removeHiddenNodes)
				.then(hideDetachedNodes)
				.then(calcWeights)
				.then(finalize)
				.then(resolve);
		}
		else {
			resolve();
		}
	});
});

const PROCESSED_DATA = Symbol();
const FILTERED_DATA = Symbol();
const FULL_NODE_INDEX = Symbol();
const NODE_INDEX = Symbol();
const NODE_TYPES = Symbol();
const FULL_LINK_INDEX = Symbol();
const LINK_INDEX = Symbol();
const IS_NODE_WEIGHT_NORMALIZED = Symbol();
const IS_LINK_WEIGHT_NORMALIZED = Symbol();
const STATS = Symbol();

export const NODE_WEIGHT_TYPES = new Enum({
	NONE: 'none',
	DONE: 'done',
	QUANT_LINKS: 'links'
});

export const LINK_WEIGHT_TYPES = new Enum({
	NONE: 'none',
	DONE: 'done',
	QUANT_MERGED: 'merged'
});

export default class GraphDB {
	constructor(settings = {}) {
		this[FULL_NODE_INDEX] = [];
		this[NODE_INDEX] = [];
		this[FULL_LINK_INDEX] = [];
		this[LINK_INDEX] = [];
		this[STATS] = {};

		forOwn(settings, (value, key) => {
			if (this[key]) {
				this[key](value);
			}
		});
	}

	data(data) {
		const self = this;

		const isLinked = (link) => {
			const linkIndexItem = getLink.call(self, link.source.id, true);
			return !!linkIndexItem && linkIndexItem.all.includes(link.target.id);
		};

		if (arguments.length) {
			const deDuplicatedLinks = [];
			let prevNodeIndex = self[FULL_NODE_INDEX];

			self[PROCESSED_DATA] = data;
			self[NODE_TYPES] = {};
			self[FULL_NODE_INDEX] = [];
			self[NODE_INDEX] = [];
			self[FULL_LINK_INDEX] = [];
			self[LINK_INDEX] = [];

			return new Promise((resolve) => {
				processData({
					data: self[PROCESSED_DATA].nodes,
					normalizeWeights: self.normalizeWeights(),
					processCallback: self.onProcessNode(),
					getItem(node) {
						return prevNodeIndex.find((d) => d.id === node.id);
					},
					eachBefore(node) {
						setNode.call(self, node, true);

						if (node.type) {
							if (!self[NODE_TYPES][node.type]) {
								self[NODE_TYPES][node.type] = 0;
							}
							self[NODE_TYPES][node.type]++;
						}

						node.weight = node.weight || 1;

						return node.weight;
					}
				})
					.then(processData({
						data: self[PROCESSED_DATA].edges,
						normalizeWeights: self.normalizeWeights(),
						processCallback: self.onProcessLink(),
						eachBefore(link) {
							let output;

							link.source = getNode.call(self, link.source, true);
							link.target = getNode.call(self, link.target, true);

							if (link.source && link.target && link.source !== link.target && !isLinked(link)) {
								setLink.call(self, link, true);

								output = link.weight = link.weight || 1;

								if (!self.isDirected()) {
									deDuplicatedLinks.push(link);
								}
							}

							return output;
						},
						between() {
							if (!self.isDirected()) {
								self[PROCESSED_DATA].edges = deDuplicatedLinks;
							}
						}
					}))
					.then(() => {
						return filter.call(self);
					})
					.then(resolve);
			});
		}

		return self[FILTERED_DATA];
	}

	filter() {
		return filter.call(this);
	}

	node(id) {
		return getNode.call(this, id);
	}

	eachNode(callback) {
		this[FILTERED_DATA].nodes.forEach(callback);
	}

	eachEdge(callback) {
		this[FILTERED_DATA].edges.forEach(callback);
	}

	get nodeTypes() {
		return this[NODE_TYPES];
	}

	get totalNodes() {
		return this[PROCESSED_DATA].nodes.length;
	}

	get totalEdges() {
		return this[PROCESSED_DATA].edges.length;
	}

	get stats() {
		return this[STATS];
	}

	get isNodeWeightNormalized() {
		return this[IS_NODE_WEIGHT_NORMALIZED];
	}

	get isLinkWeightNormalized() {
		return this[IS_LINK_WEIGHT_NORMALIZED];
	}

	linkCount(node) {
		const link = getLink.call(this, node.id);
		return link ? link.all.length : 0;
	}

	hasLinks(node) {
		return this.linkCount(node) > 0;
	}

	linkedNodes(node) {
		const link = getLink.call(this, node.id);
		return !link ? [] : link.all.map((id) => getNode.call(this, id));
	}

	shortestPaths(source, target) {
		const self = this;
		let currentShortest = Infinity;
		let distances = new List().sorter(List.sorter.id.asc);

		const processNode = (node, distance) => {
			let paths = [];
			let localShortest = Infinity;
			let checkFurther = [];
			const link = getLink.call(this, node);

			if (link && link.all) {
				link.all.forEach((linkedNode) => {
					const thisDistance = distances.find({id: linkedNode});

					if (thisDistance === undefined || distance <= thisDistance.d) {
						if (thisDistance) {
							thisDistance.d = distance;
						}
						else {
							distances.add({
								id: linkedNode,
								d: distance
							});
						}

						if (linkedNode === target.id) {
							currentShortest = distance;
							paths = [[node, linkedNode]];
							return false;
						}
						else if (distance < currentShortest && self.hasLinks({id: linkedNode})) {
							checkFurther.push(linkedNode);
						}
					}
				});
			}

			for (let index = 0, length = checkFurther.length; index < length; index++) {
				const output = processNode(checkFurther[index], distance + 1);

				for (let outputIndex = 0, outputLength = output.length; outputIndex < outputLength; outputIndex++) {
					if (output[outputIndex].length < localShortest) {
						localShortest = output[outputIndex].unshift(node);
						paths.push(output[outputIndex]);
					}
				}
			}

			if (distance === 1) {
				distances = null;
			}

			return paths.filter((path) => path.length <= localShortest);
		};

		distances.add({
			id: source.id,
			d: 0
		});

		return new Promise((resolve) => {
			resolve(processNode(source.id, 1)
				.map((path) => path.map((node) => (node.id ? node : getNode.call(this, node)))));
		});
	}

	isLinked(node1, node2, maxDepth = 1) {
		const self = this;

		const checkLink = (node, depth) => {
			const link = getLink.call(self, node.id);
			let isLink = link && link.all.includes(node2.id);

			if (!isLink && depth < maxDepth && link && link.all) {
				link.all.forEach((linkedNode) => {
					isLink = checkLink(getNode.call(this, linkedNode), depth + 1);
					return !isLink;
				});
			}

			return isLink;
		};

		return node1 === node2 || checkLink(node1, 1);
	}
}

Object.assign(GraphDB.prototype, {
	onFilter: methodFunction(),
	onProcessNode: methodFunction(),
	onProcessLink: methodFunction(),
	isDirected: methodBoolean(),
	normalizeWeights: methodBoolean(),
	hiddenNodeTypes: methodArray({
		set: filter
	}),
	filterFunc: methodFunction(),
	calcNodeWeightBy: methodEnum({
		enum: NODE_WEIGHT_TYPES,
		init: NODE_WEIGHT_TYPES.NONE,
		set: filter
	}),
	calcLinkWeightBy: methodEnum({
		enum: LINK_WEIGHT_TYPES,
		init: LINK_WEIGHT_TYPES.NONE,
		set: filter
	}),
	hideDetachedNodes: methodBoolean({
		set: filter
	})
});
