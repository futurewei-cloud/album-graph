import { scaleLinear } from 'd3';
import FrameRateHistory from 'framerate-history';
import './FrameRate.less';

const PADDING = 1.5;
const SAMPLE_RATE = 8;
const DURATION = 30;

const buildPath = function(data) {
	return 'M' + data.map((d, i) => {
		return this[SCALE_X](i) + ',' + this[SCALE_Y](d) + (i ? '' : 'L');
	}).join(' ');
};

const buildSparkLine = function(container, width, height) {
	const xMax = width - PADDING;
	const yMax = height - (PADDING * 2);

	const buildLine = (y) => {
		return 'M' + xMax + ',' + (y + PADDING) + 'L0,' + (y + PADDING) + ' ';
	};

	this[SCALE_X] = scaleLinear()
		.range([0, xMax])
		.domain([0, (SAMPLE_RATE * DURATION) - 1]);
	this[SCALE_Y] = scaleLinear()
		.range([yMax + PADDING, PADDING])
		.domain([0, 60]);

	this[BASELINE] = ' ' + xMax + ',' + (yMax + PADDING) + ' 0,' + (yMax + PADDING) + 'z';

	const svg = container
		.append('svg')
		.attr('class', 'framerate')
		.attr('width', width)
		.attr('height', height);
	svg.append('path')
		.style('fill', 'none')
		.attr('d', buildLine(0) + buildLine(yMax));
	this[PATH] = svg.append('path')
		.attr('class', 'line');
	this[FILL] = svg.append('path')
		.attr('class', 'fill');
	this[CIRCLE] = svg.append('circle')
		.attr('class', 'circle')
		.attr('r', 1.5);

	this[TEXT] = svg.append('text')
		.attr('x', width - 5)
		.attr('y', height - 5)
		.attr('class', 'text');
};

const updateSparkLine = function(data) {
	const line = buildPath.call(this, data);

	this[PATH]
		.attr('d', line);
	this[FILL]
		.attr('d', line + this[BASELINE]);
	this[CIRCLE]
		.attr('cx', this[SCALE_X](data.length - 1))
		.attr('cy', this[SCALE_Y](data[data.length - 1]));
	this[TEXT]
		.text(data[data.length - 1] + ' fps');
};

const SCALE_X = Symbol();
const SCALE_Y = Symbol();
const BASELINE = Symbol();
const PATH = Symbol();
const FILL = Symbol();
const CIRCLE = Symbol();
const TEXT = Symbol();
const FPS = Symbol();

export default class FrameRate {
	constructor(container) {
		const self = this;

		buildSparkLine.call(self, container, 172, 32);

		self[FPS] = new FrameRateHistory({
			sampleRate: SAMPLE_RATE,
			historyDuration: DURATION,
			onSample(history) {
				updateSparkLine.call(self, history);
			}
		});
	}
}
