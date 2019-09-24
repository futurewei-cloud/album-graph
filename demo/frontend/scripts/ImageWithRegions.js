import { forOwn } from 'object-agent';
import { method } from 'type-enforcer';
import './ImageWithRegions.less';

const WRAPPER = Symbol();
const IMAGE = Symbol();
const REGIONS = Symbol();
const WIDTH = Symbol();
const HEIGHT = Symbol();

const percent = (pos, total) => {
	return ((pos / total) * 100) + '%';
};

const setRegions = function(regions) {
	const self = this;

	if (self[REGIONS]) {
		self[REGIONS].forEach((region) => {
			region.remove();
		});
	}
	self[REGIONS] = [];

	regions.forEach((region) => {
		const container = document.createElement('div');
		container.style.left = percent(region.left, self[WIDTH]);
		container.style.width = percent(region.width, self[WIDTH]);
		container.style.top = percent(region.top, self[HEIGHT]);
		container.style.height = percent(region.height, self[HEIGHT]);
		if (region.isValid) {
			container.classList.add('valid');
		}
		if (region.isError) {
			container.classList.add('error');
		}

		if (region.label) {
			const label = document.createElement('div');
			label.textContent = region.label;
			container.appendChild(label);
		}

		self[WRAPPER].appendChild(container);

		self[REGIONS].push(container);
	});
};

export default class ImageWithRegions {
	constructor(settings) {
		this[WRAPPER] = document.createElement('div');
		this[IMAGE] = document.createElement('img');
		this[WIDTH] = 0;
		this[HEIGHT] = 0;

		this[WRAPPER].appendChild(this[IMAGE]);
		this[WRAPPER].classList.add('image-wrapper');
		if (settings.container) {
			settings.container.appendChild(this[WRAPPER]);
		}

		forOwn(settings, (value, key) => {
			if (this[key]) {
				this[key](value);
			}
		});
	}

	remove() {
		this.regions([]);
		this[IMAGE].remove();
		this[WRAPPER].remove();
	}
}

Object.assign(ImageWithRegions.prototype, {
	src: method.string({
		set: function(src) {
			const onLoad = () => {
				this[WIDTH] = this[IMAGE].naturalWidth;
				this[HEIGHT] = this[IMAGE].naturalHeight;
				this[IMAGE].removeEventListener('load', onLoad);
				setRegions.call(this, this.regions());
			};
			this[IMAGE].addEventListener('load', onLoad);
			this[IMAGE].src = src;
		}
	}),
	regions: method.array({
		set: function(regions) {
			setRegions.call(this, regions);
		}
	})
});
