import { formatDistanceToNow, formatRelative, isValid } from 'date-fns';
import { Container, Div, Heading, HEADING_LEVELS, IS_DESKTOP, Picker, Slider, Timeline, TooltipMixin } from 'hafgufa';
import { Collection, compare, Model } from 'hord';
import { applySettings, CssSize, DockPoint, methodArray, methodFunction } from 'type-enforcer-ui';
import './FilterView.less';
import { DATE_ICON, LOCATION_ICON, PERSON_ICON, TAG_ICON } from './icons';

const toPercent = (value) => (Math.round(value * 10000) / 100) + '%';
const textHeight = new CssSize('1.4em');

class TooltipDiv extends TooltipMixin(Div) {
}

const eventModel = new Model({
	date: {
		type: Date,
		isRequired: true,
		index: true
	},
	images: Array,
	'*': '*'
});

const EVENT_CONTAINER_ID = 'event_container';
const TIMELINE_HEADING_ID = 'mainTimelineHeadingId';
const MAIN_TIMELINE_ID = 'mainTimelineId';
const TIMELINE_SLIDER_ID = 'timelineSliderId';
const DENSITY_TIMELINE_ID = 'densityTimelineId';
const PICKER_CONTAINER_ID = 'pickerContainerId';
const LOCATION_PICKER_ID = 'locationPickerId';
const PERSON_PICKER_ID = 'personPickerId';
const TAG_PICKER_ID = 'tagPickerId';

const EVENTS = Symbol();
const MAX_EVENT_SIZE = Symbol();

const buildDisplayDate = Symbol();
const renderMainTimeSpan = Symbol();
const updateDensityGraphRange = Symbol();
const triggerChange = Symbol();

export default class FilterView extends Div {
	constructor(settings = {}) {
		settings.type = 'timeline';

		super(settings);

		const self = this;
		const now = new Date();
		const yesterday = new Date();
		yesterday.setFullYear(yesterday.getFullYear() - 1);

		self.addClass('filter-view');
		textHeight.element(self.element);

		self.content([{
			control: Heading,
			id: TIMELINE_HEADING_ID,
			level: HEADING_LEVELS.FIVE,
			title: 'When',
			icon: DATE_ICON,
			classes: 'time'
		}, {
			control: Container,
			height: '4em',
			width: '100%',
			margin: '0 0 0.5em 0',
			css: {
				'overflow': 'visible'
			},
			content: [{
				control: Timeline,
				id: MAIN_TIMELINE_ID,
				height: '100%',
				width: '100%',
				padding: '0 0.75rem',
				onSpanRender(control, data) {
					self[renderMainTimeSpan](control, data, '2.1em');
				},
				dateStart: yesterday,
				dateEnd: now,
				lineOffset: '-1.5em',
				canZoom: false
			}, {
				control: Slider,
				id: TIMELINE_SLIDER_ID,
				classes: 'timeline-slider',
				height: '100%',
				width: '100%',
				min: yesterday.valueOf(),
				max: now.valueOf(),
				value: [yesterday.valueOf(), now.valueOf()],
				canDragRange: true,
				onSlide(newValue) {
					self[updateDensityGraphRange](Math.round(newValue[0]), Math.round(newValue[1]));
				},
				onChange() {
					self[triggerChange]();
				},
				buildTooltip(value) {
					return FilterView[buildDisplayDate](value);
				}
			}]
		}, {
			control: Timeline,
			id: DENSITY_TIMELINE_ID,
			height: '9em',
			width: '100%',
			padding: '0 0.75rem',
			onSpanRender(control, data) {
				self[renderMainTimeSpan](control, data, '6.8em');
			},
			lineOffset: '-1.8em',
			canZoom: false,
			showButtons: false
		}, {
			control: Container,
			id: PICKER_CONTAINER_ID,
			content: [{
				control: Picker,
				id: LOCATION_PICKER_ID,
				classes: 'location',
				title: 'Where',
				headingIcon: LOCATION_ICON,
				width: '100%',
				singleLine: IS_DESKTOP,
				showAll: true,
				onChange() {
					self[triggerChange]();
				}
			}, {
				control: Picker,
				id: PERSON_PICKER_ID,
				classes: 'person',
				title: 'Who',
				headingIcon: PERSON_ICON,
				width: '100%',
				singleLine: IS_DESKTOP,
				showAll: true,
				onChange() {
					self[triggerChange]();
				}
			}, {
				control: Picker,
				id: TAG_PICKER_ID,
				classes: 'tag',
				title: 'What',
				headingIcon: TAG_ICON,
				width: '100%',
				singleLine: IS_DESKTOP,
				showAll: true,
				onChange() {
					self[triggerChange]();
				}
			}]
		}]);

		applySettings(self, settings);

		self
			.onResize(() => {
				self.get(TIMELINE_SLIDER_ID).resize(true);
			})
			.resize();
	}

	static [buildDisplayDate](date) {
		const now = new Date();
		date = new Date(date);

		return isValid(date) ? `${formatRelative(date, now)} (${formatDistanceToNow(date)} ago)` : '';
	}

	[renderMainTimeSpan](control, data, height) {
		const self = this;
		const length = data.end - data.start;
		const eventContainer = control.get(EVENT_CONTAINER_ID) || new Div({
			container: control,
			id: EVENT_CONTAINER_ID,
			height: height,
			css: {
				overflow: 'visible'
			}
		});

		eventContainer.content(data.events.map((event) => {
			return {
				control: TooltipDiv,
				classes: 'event',
				tooltipDockPoint: DockPoint.POINTS.BOTTOM_CENTER,
				tooltip: `${FilterView[buildDisplayDate](event.date)}<br>${event.images.length} photos`,
				height: toPercent(event.images.length / self[MAX_EVENT_SIZE]),
				minHeight: '3px',
				css: {
					left: toPercent((event.date - data.start) / length)
				}
			};
		}));
	}

	[updateDensityGraphRange](start, end) {
		const self = this;

		self.get(DENSITY_TIMELINE_ID)
			.dateStart(new Date(start))
			.dateEnd(new Date(end));
	}

	[triggerChange]() {
		const self = this;
		const slider = self.get(TIMELINE_SLIDER_ID);
		const sliderValue = slider.value().map((value) => Math.round(value));

		self.onChange()({
			when: (Math.round(slider.min()) !== sliderValue[0] || Math.round(slider.max()) !== sliderValue[1]) ? sliderValue : [],
			where: self.get(LOCATION_PICKER_ID).value(),
			who: self.get(PERSON_PICKER_ID).value(),
			what: self.get(TAG_PICKER_ID).value()
		});
	}

	events(events) {
		const self = this;

		self[EVENTS] = events = new Collection(events)
			.sort(compare('date'))
			.model(eventModel);

		self[MAX_EVENT_SIZE] = 0;
		events.forEach((event) => {
			self[MAX_EVENT_SIZE] = Math.max(self[MAX_EVENT_SIZE], event.images.length);
		});

		self.get(MAIN_TIMELINE_ID)
			.dateStart(null)
			.dateEnd(null)
			.data(events);
		self.get(DENSITY_TIMELINE_ID).data(events);

		const minDate = events.first().date.valueOf();
		const maxDate = events.last().date.valueOf();

		self.get(TIMELINE_SLIDER_ID)
			.min(minDate)
			.max(maxDate)
			.value([minDate, maxDate]);

		self[updateDensityGraphRange](minDate, maxDate);
	}
}

Object.assign(FilterView.prototype, {
	tags: methodArray({
		set(tags) {
			this.get(TAG_PICKER_ID).options({
				isMultiSelect: true,
				children: tags
			});
		}
	}),
	locations: methodArray({
		set(locations) {
			this.get(LOCATION_PICKER_ID).options({
				isMultiSelect: true,
				children: locations
			});
		}
	}),
	people: methodArray({
		set(people) {
			this.get(PERSON_PICKER_ID).options({
				isMultiSelect: true,
				children: people
			});
		}
	}),
	onChange: methodFunction()
});
