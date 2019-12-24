import { delay } from 'async-agent';
import { formatRelative } from 'date-fns';
import { Container, Drawer, LocalHistory, Section, theme } from 'hafgufa';
import { clone } from 'object-agent';
import { windowResize } from 'type-enforcer-ui';
import config from '../graph.config';
import './app.less';
import FilterView from './FilterView';
import ForceGraph from './graph/ForceGraph';
import Header from './Header';
import Load from './Load';
import SelectionPanel from './SelectionPanel';

const SMALL_SET_SIZE = 200;
const LARGE_SET_SIZE = 4365;
const CURRENT_SET_SIZE = SMALL_SET_SIZE;

const FORCE_GRAPH = Symbol();
const LOAD = Symbol();
const HISTORY = Symbol();
const CONTROL_LAYER = Symbol();
const HEADER = Symbol();
const SELECTION_PANEL = Symbol();
const FILTER_VIEW = Symbol();
const HAS_FILTER_DATA = Symbol();
const FILTER_DATA = Symbol();
const DATA = Symbol();

class App {
	constructor() {
		const self = this;

		theme
			.path('[name].[env].min.css')
			.themes(['moonBeam.dark', 'moonBeam.light'])
			.theme('moonBeam.dark');

		self[HAS_FILTER_DATA] = false;
		self[FILTER_DATA] = {
			when: [],
			where: [],
			who: [],
			what: []
		};

		self.buildLoad();
		self.startHistory();
		self.buildForceGraph();
		self.buildControlLayer();
		self.loadRandom();
	}

	buildLoad() {
		const self = this;
		let isFirst = true;

		self[LOAD] = new Load(config)
			.onQuery(() => {
				self[HEADER].isWorking(true);
				isFirst = true;
			})
			.onLoad((data) => {
				self[DATA] = data;
				self[FORCE_GRAPH]
					.data(clone(data))
					.then(() => {
						if (isFirst) {
							delay(() => {
								self[FORCE_GRAPH].zoom('selected');
							}, 100);
							isFirst = false;
						}
					});
			})
			.onDone(() => {
				self[HEADER].isWorking(false);
			})
			.onLoadSearch((suggestions) => {
				self[HEADER].suggestions(suggestions);
				if (self[FILTER_VIEW]) {
					self[FILTER_VIEW].tags(suggestions.filter((suggestion) => suggestion.classes === 'tag'));
					self[FILTER_VIEW].locations(suggestions.filter((suggestion) => suggestion.classes === 'location'));
					self[FILTER_VIEW].people(suggestions.filter((suggestion) => suggestion.classes === 'person'));
				}
			})
			.onLoadEvents((events) => {
				self[FILTER_VIEW].events(events);
			});
	}

	loadRandom() {
		this[HISTORY].push([Math.round(Math.random() * CURRENT_SET_SIZE).toString()]);
	}

	startHistory() {
		const self = this;
		const applyHistory = (historyObject) => self[LOAD].query(...historyObject);

		self[HISTORY] = new LocalHistory({
			onPush: applyHistory,
			onUndo: applyHistory,
			max: 50
		});
	}

	buildForceGraph() {
		const self = this;

		self[FORCE_GRAPH] = new ForceGraph({
			container: document.body,
			onSelectionChange(selectedNodes) {
				self[SELECTION_PANEL].selection(selectedNodes);
			},
			padding: '60 264 40 40',
			onNodeClick(node) {
				let query = node.id;
				let extraArg;

				if (node.type === 'location') {
					query = node.label;
					extraArg = node.locationType;
				}
				if (node.type === 'time') {
					extraArg = 'time';
				}

				self[HISTORY].push([query, extraArg]);
			},
			filterFunc(node) {
				if (self[HAS_FILTER_DATA] && node.type === 'image') {
					let result = true;

					if (self[FILTER_DATA].when.length !== 0) {
						if (!node.meta.datetime) {
							return false;
						}
						const date = new Date(node.meta.datetime).valueOf();

						result = result && !(date < self[FILTER_DATA].when[0] || date > self[FILTER_DATA].when[1]);
					}

					result = result && self[FILTER_DATA].where.every((item) => {
						return node.meta.location && node.meta.location.includes(item.title);
					});

					result = result && self[FILTER_DATA].who.every((item) => {
						return node.meta.person && node.meta.person.includes(item.title);
					});

					result = result && self[FILTER_DATA].what.every((item) => {
						return node.meta.tag && node.meta.tag.includes(item.id);
					});

					return result;
				}

				return true;
			},
			labelExtent: 0,
			labelExtentOnMouseOver: 0,
			singleSelect: true,
			showLabelsOnNodes: true,
			hideDetachedNodes: true,
			...config.graphSettings
		});

		windowResize.add((width, height) => {
			self[FORCE_GRAPH]
				.height(height)
				.width(width);
		});
	}

	buildControlLayer() {
		const self = this;

		self[CONTROL_LAYER] = new Container({
			container: document.body,
			classes: 'control-layer'
		});

		self[HEADER] = new Header({
			container: self[CONTROL_LAYER],
			title: config.projectName,
			onSearch(value) {
				if (value === 'random') {
					self.loadRandom();
				}
				else if (value === 'undo') {
					self[HISTORY].undo();
				}
				else {
					self[HISTORY].push([value]);
				}
			},
			forceGraph: self[FORCE_GRAPH]
		});

		self[SELECTION_PANEL] = new SelectionPanel({
			container: self[CONTROL_LAYER],
			forceGraph: self[FORCE_GRAPH],
			onUnSelect(node) {
				self[FORCE_GRAPH].select(node);
			}
		});

		const FILTER_SECTION_ID = 'filterSection';
		const FILTER_VIEW_ID = 'filterView';
		const filterDrawerOpenDefault = false;

		const eventDrawer = new Drawer({
			container: self[CONTROL_LAYER],
			dock: 'bottom',
			canResize: false,
			overlap: Drawer.OVERLAP.ALWAYS,
			isOpen: filterDrawerOpenDefault,
			height: '90vh',
			maxHeight: '25rem',
			closedSize: '2.2em',
			isAnimated: true,
			content: [{
				control: Section,
				id: FILTER_SECTION_ID,
				title: 'Filters',
				headingIcon: '',
				height: '100%',
				padding: '0 1.25rem 1.25rem',
				isCollapsed: !filterDrawerOpenDefault,
				onCollapse() {
					eventDrawer.isOpen(!this.isCollapsed());
					delay(() => {
						self[FILTER_VIEW].resize(true);
					});
				},
				content: {
					control: FilterView,
					id: FILTER_VIEW_ID,
					width: '100%',
					onChange(data) {
						let subTitle = '';

						self[HAS_FILTER_DATA] = false;

						if (data.when.length !== 0) {
							self[HAS_FILTER_DATA] = true;
							subTitle += formatRelative(data.when[0], new Date()) + ' to ' + formatRelative(data.when[1], new Date());
						}

						['where', 'who', 'what'].forEach((key) => {
							if (data[key].length !== 0) {
								self[HAS_FILTER_DATA] = true;
								if (subTitle !== '') {
									subTitle += ' and ';
								}

								subTitle += key.toUpperCase() + ': ' + data[key].map((value) => value.title).join(', ');
							}
						});

						eventDrawer.get(FILTER_SECTION_ID).subTitle(subTitle);

						self[FILTER_DATA] = data;

						self[FORCE_GRAPH].data(clone(self[DATA]));
					}
				}
			}]
		});

		self[FILTER_VIEW] = eventDrawer.get(FILTER_VIEW_ID);
	}
}

new App();
