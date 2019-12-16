import { forceCollide, forceLink, forceManyBody, forceSimulation, forceX, forceY } from 'd3';
import { method } from 'type-enforcer-ui';

const SIMULATION = Symbol();
const GRAPH_DB = Symbol();
const CHARGE = 'charge';
const CHARGE_FORCE = 'charge';
const LINK_FORCE = 'links';
const COLLISION_FORCE = 'collision';
const X_FORCE = 'x';
const Y_FORCE = 'y';

export default class Simulation {
	constructor(graphDb) {
		const self = this;

		self[GRAPH_DB] = graphDb;

		this[SIMULATION] = forceSimulation()
			.force(CHARGE_FORCE, forceManyBody().strength((d) => {
				return d.r * this[CHARGE] * (d.extraCharge || 1);
			}))
			.force(LINK_FORCE, forceLink())
			.force(X_FORCE, forceX().strength(this.xStrength()))
			.force(Y_FORCE, forceY().strength(this.yStrength()))
			.force(COLLISION_FORCE, forceCollide().radius((d) => d.rPlus))
			.on('tick', () => self.onTick()())
			.alphaMin(0.0001);
	}

	refresh(data) {
		data = data || {
			nodes: this.nodes(),
			edges: this.links()
		};

		this[CHARGE] = Math.pow(data.edges.length / data.nodes.length, 2) * -this.nodeCharge();
		const linkStrength = this.linkStrength();

		this[SIMULATION].nodes(data.nodes, (d) => d.id);

		this[SIMULATION].force(LINK_FORCE)
			.id((d) => d.id)
			.strength((d) => {
				return (d.weight + linkStrength) * (1 / Math.min(
					this[GRAPH_DB].linkCount(d.source),
					this[GRAPH_DB].linkCount(d.target)
				));
			})
			.links(data.edges);

		this.bump();
	}

	nodes() {
		return this[SIMULATION].nodes();
	}

	links() {
		return this[SIMULATION].force(LINK_FORCE).links();
	}

	pause() {
		this[SIMULATION]
			.stop()
			.alpha(0.1);
	}

	bump() {
		if (this[SIMULATION].alpha() <= this[SIMULATION].alphaMin()) {
			this[SIMULATION].alpha(this[SIMULATION].alphaMin() + 0.001);
		}
		this[SIMULATION].restart();
	}

	startPerpetual() {
		this[SIMULATION].alphaTarget(0.3).restart();
	}

	stopPerpetual() {
		this[SIMULATION].alphaTarget(0);
	}
}

Object.assign(Simulation.prototype, {
	onTick: method.function(),
	nodeCharge: method.number({
		init: 20,
		min: 0
	}),
	linkStrength: method.number({
		init: 0.25
	}),
	xStrength: method.number({
		init: 0.1,
		min: 0,
		max: 1,
		set(xStrength) {
			this[SIMULATION].force(X_FORCE).strength(xStrength);
		}
	}),
	yStrength: method.number({
		init: 0.1,
		min: 0,
		max: 1,
		set(yStrength) {
			this[SIMULATION].force(Y_FORCE).strength(yStrength);
		}
	})
});
