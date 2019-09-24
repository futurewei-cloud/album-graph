const MIN = Symbol();
const MAX = Symbol();
const OFFSET = Symbol();

export default class WeightNormalizer {
	constructor() {
		this.reset();
	}

	add(weight) {
		if (!this[MIN]) {
			this[MIN] = weight;
		}
		this[MIN] = (this[MIN] < weight) ? this[MIN] : weight;
		this[MAX] = (this[MAX] > weight) ? this[MAX] : weight;
	}

	done() {
		this[OFFSET] = this[MAX] - this[MIN];
	}

	calc(weight) {
		return this[OFFSET] ? (weight - this[MIN]) / this[OFFSET] : 1;
	}

	reset() {
		this[MIN] = 0;
		this[MAX] = 0;
		this[OFFSET] = 0;

		return this;
	}

	normalize(items, callback) {
		this.reset();

		items.forEach((item) => this.add(item.weight = callback(item)));

		this.done();

		items.forEach((item) => item.weight = this.calc(item.weight));

		return !!this[OFFSET];
	}
}
