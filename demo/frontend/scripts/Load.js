import { debounce } from 'async-agent';
import { json } from 'd3';
import { IS_PHONE } from 'hafgufa';
import { List } from 'hord';
import { clone, forOwn, isEmpty } from 'object-agent';
import { castArray, enforceDate, isDate, isNumber, isString, method } from 'type-enforcer-ui';
import { DATE_ICON, LOCATION_ICON, PERSON_ICON, SEMANTIC_ICON, TAG_ICON } from './icons';

const TARGET_IMAGES = IS_PHONE ? 50 : 100;
const DATE_SEPARATOR = '/';
const DATASET = 's';

const clamp = (num, min, max) => num < min ? min : num > max ? max : num;

const lengthSort = (a, b) => b.length - a.length;

const selectedProps = {
	isSelected: true
};

const getExtraProps = (isPrimary) => {
	return isPrimary ? selectedProps : null;
};

let config;
const NODE_IDS = Symbol();
const LOADING_TAGS = Symbol();
const LOADED_TAGS = Symbol();
const CACHE = Symbol();
const ALL_SUGGESTIONS = Symbol();
const ALL_TAGS = Symbol();
const ALL_TAGS_LOWERCASE = Symbol();
const PEOPLE = Symbol();
const EVENTS = Symbol();

const reset = Symbol();
const saveImage = Symbol();
const saveMeta = Symbol();
const saveImages = Symbol();
const loadImages = Symbol();
const loadTagImages = Symbol();
const loadSemanticImages = Symbol();
const loadLocationImages = Symbol();
const loadDateImages = Symbol();
const loadPersonImages = Symbol();

export default class Load {
	constructor(data) {
		const self = this;

		const emitSuggestions = debounce(() => {
			if (self.onLoadSearch()) {
				self.onLoadSearch()(clone(self[ALL_SUGGESTIONS].values()));
			}
		});

		const addSuggestions = (items, icon, classes) => {
			castArray(items).forEach((item) => {
				if (item) {
					if (isString(item)) {
						item = {
							title: item,
							subTitle: ''
						};
					}

					if (!item.id) {
						item.id = item.title.replace(/ /g, '_');
					}
					if (icon && !item.icon) {
						item.icon = icon;
					}
					if (classes && !item.classes) {
						item.classes = classes;
					}

					self[ALL_SUGGESTIONS].addUnique(item);
				}
			});

			emitSuggestions();
		};

		const loadAllTags = () => {
			Load.loadJson('alltags', 'arg=NA')
				.then((tags) => {
					self[ALL_TAGS] = tags.sort(lengthSort);
					self[ALL_TAGS_LOWERCASE] = tags.map((tag) => tag.toLocaleLowerCase());

					addSuggestions(self[ALL_TAGS], TAG_ICON, 'tag');
				});
		};

		const loadRelationships = () => {
			Load.loadJson('allrelationships', 'arg=NA')
				.then((data) => {
					data.forEach((words) => {
						addSuggestions(words.join(' '), SEMANTIC_ICON, 'semantic');
					});
				});
		};

		const loadLocation = (need, type) => {
			Load.loadJson(need, 'arg=NA')
				.then((data) => {
					data.forEach((location) => {
						addSuggestions({
							id: location.replace(' ', '_') + '~' + type,
							title: location,
							subTitle: type
						}, LOCATION_ICON, 'location');
					});
				});
		};

		const loadPeople = (clusterId) => {
			Load.getPersonImages(clusterId)
				.then((images) => {
					if (!isEmpty(images)) {
						const label = 'Person ' + clusterId;

						self[CACHE][label] = images;
						loadPeople(clusterId + 1);

						self[PEOPLE].push({
							tag: label,
							clusterId: clusterId,
							images: Object.keys(images)
						});

						addSuggestions(label, PERSON_ICON, 'person');
					}
				});
		};

		const loadEvents = () => {
			let eventLoadCount = 0;
			let eventLoadId = 0;
			let isDone = false;

			const loadChunk = () => {
				if (!eventLoadCount) {
					if (isDone) {
						if (self.onLoadEvents()) {
							self.onLoadEvents()(self[EVENTS]);
						}
					}
					else {
						for (let index = 0; index < 10; index++) {
							eventLoadCount++;
							eventLoadId++;
							load(eventLoadId);
						}
					}
				}
			};

			const load = (id) => {
				Load.getEventImages(id)
					.then((images) => {
						const minDate = new Date('9/1/2010').valueOf();
						const maxDate = new Date().valueOf();

						eventLoadCount--;

						if (!isEmpty(images)) {
							const label = 'Event ' + id;

							images = Object.keys(images);

							if (!isEmpty(images)) {
								self[CACHE][label] = images;

								self[EVENTS].push({
									tag: label,
									id: id,
									date: id === 1 ? new Date() : new Date(Math.round(Math.random() * (maxDate - minDate)) + minDate),
									images: images
								});

								addSuggestions(label, DATE_ICON, 'event');
							}

						}
						else {
							isDone = true;
						}

						loadChunk();
					});
			};

			loadChunk();
		};

		config = data;
		self[ALL_SUGGESTIONS] = new List().sorter(List.sorter.id.asc);
		self[ALL_TAGS] = [];
		self[ALL_TAGS_LOWERCASE] = [];
		self[EVENTS] = [];
		self[PEOPLE] = [];
		self[CACHE] = {};
		self[CACHE].specs = {};
		self[NODE_IDS] = [];
		self[LOADED_TAGS] = 0;
		self[LOADING_TAGS] = 0;

		loadAllTags();
		loadRelationships();
		loadLocation('allcities', 'city');
		loadLocation('allstates', 'state');
		loadLocation('allcountries', 'country');
		loadPeople(0);
		loadEvents();
	}

	static loadJson(need, params) {
		return json(`${config.apiUrl}albumgraph?need=${need}&${params}&dataset=${DATASET}`);
	}

	static getImageSpecs(id) {
		return Load.loadJson('img', `output=allimginfo&arg=${id}`);
	}

	static getTags(id) {
		return Load.loadJson('img', `output=tag&arg=${id}`);
	}

	static getRelationships(id) {
		return Load.loadJson('img', `output=relationships&arg=${id}`);
	}

	static getAllImages(tag) {
		return Load.loadJson('tag', `arg=${tag}`);
	}

	static getRecommendedImages(tag, imagesPerTag) {
		return Load.loadJson('recommendation', `arg=${tag}&num=${imagesPerTag}`);
	}

	static getLocationImages(location, locationType) {
		return Load.loadJson(locationType, `arg=${location}`);
	}

	static getDateImages(start, end) {
		return Load.loadJson('date', `start=${start}&end=${end}`);
	}

	static getPersonImages(id) {
		return Load.loadJson('cluster', `arg=${id}`);
	}

	static getSemanticImages(words) {
		return Load.loadJson('semantic', `subj=${words[0]}&predicate=${words[1]}&obj=${words[2]}`);
	}

	static getEventImages(id) {
		return Load.loadJson('event', `arg=${id}`);
	}

	static buildImageUrl(src, size = 'm') {
		return `${config.apiUrl}${size}images?prefix=${src.replace(/(\/)(?!.*\1)/, '/&filename=')}&cachebust=3`;
	}

	[reset]() {
		this[NODE_IDS].length = 0;

		this[LOADING_TAGS] = 1;
		this[LOADED_TAGS] = 0;

		this.data = {
			nodes: [],
			edges: []
		};

		return this;
	}

	[saveImage](image, imageId, isSelected, meta = {}) {
		if (!this[NODE_IDS].includes(imageId)) {
			const data = {
				id: imageId,
				image: {
					small: Load.buildImageUrl(image, 's'),
					medium: Load.buildImageUrl(image, 'm'),
					large: Load.buildImageUrl(image, 'l')
				},
				selectedNodeZoom: 5,
				type: 'image',
				weight: 0.3,
				meta: meta
			};

			if (isSelected) {
				data.isSelected = true;
				data.x = 0;
				data.y = 0;
			}

			this.data.nodes.push(data);
			this[NODE_IDS].push(imageId);

			return true;
		}

		return false;
	}

	[saveImages](sourceId, tag, type, images, max, extraProperties = {}, icon = '') {
		const self = this;
		let count = 0;

		self.data.nodes.push({
			id: tag,
			type: type,
			label: tag,
			icon: icon,
			classes: type,
			weight: 1,
			...extraProperties
		});

		if (sourceId) {
			self[saveMeta](sourceId, type, tag);

			self.data.edges.push({
				source: sourceId,
				target: tag,
				weight: 1
			});
		}

		forOwn(images, (image, imageId) => {
			if (count < max) {
				if (self[saveImage](image, imageId, false)) {
					count++;
				}

				self.data.nodes.forEach((node) => {
					if (self[CACHE][node.id] && self[CACHE][node.id][imageId]) {
						self.data.edges.push({
							source: imageId,
							target: node.id,
							weight: 1
						});
					}
				});
			}
		});

		self.onLoad()(clone(self.data));

		self[LOADED_TAGS]++;
		if (self[LOADED_TAGS] === self[LOADING_TAGS]) {
			self.onDone()();
		}
	}

	[saveMeta](sourceId, type, tag) {
		const sourceNode = this.data.nodes.find((node) => node.id === sourceId);
		if (!sourceNode.meta[type]) {
			sourceNode.meta[type] = [];
		}
		if (!sourceNode.meta[type].includes(tag)) {
			sourceNode.meta[type].push(tag);
		}
	}

	[loadImages](settings) {
		const self = this;

		const done = () => {
			self[saveImages](
				settings.sourceId,
				settings.name,
				settings.type,
				self[CACHE][settings.name],
				settings.imagesPerTag,
				{
					...settings.extraProps,
					...getExtraProps(settings.isPrimary)
				},
				settings.icon
			);
		};

		if (self[CACHE][settings.name]) {
			done();
		}
		else {
			settings.loadFunction(settings.loadQuery || settings.name, settings.loadArg)
				.then((images) => {
					self[CACHE][settings.name] = images;
					done();
				});
		}
	}

	[loadTagImages](sourceId, tag, imagesPerTag, isPrimary) {
		this[loadImages]({
			loadFunction: Load.getAllImages,
			sourceId: sourceId,
			name: tag,
			type: 'tag',
			imagesPerTag: imagesPerTag,
			isPrimary: isPrimary,
			icon: TAG_ICON
		});
	}

	[loadSemanticImages](sourceId, words, imagesPerTag, isPrimary) {
		const self = this;
		const displayWords = words.join(' ');

		if (isPrimary) {
			this[loadImages]({
				loadFunction: Load.getSemanticImages,
				sourceId: sourceId,
				name: displayWords,
				loadQuery: words,
				type: 'semantic',
				imagesPerTag: imagesPerTag,
				icon: SEMANTIC_ICON,
				isPrimary: isPrimary
			});
		}
		else {
			self.data.nodes.push({
				id: displayWords,
				type: 'semantic',
				label: words[1],
				classes: 'semantic',
				icon: SEMANTIC_ICON,
				weight: 0.1
			});
			self[saveMeta](sourceId, 'semantic', displayWords);

			self.data.edges.push({
				source: sourceId,
				target: displayWords,
				weight: 0.0001,
				style: 'line',
				classes: 'semantic'
			});
			self.data.edges.push({
				source: words[0],
				target: displayWords,
				weight: 0.15,
				style: 'arrow',
				classes: 'semantic'
			});
			self.data.edges.push({
				source: displayWords,
				target: words[2],
				weight: 0.15,
				style: 'arrow',
				classes: 'semantic'
			});
		}
	}

	[loadLocationImages](sourceId, location, type, imagesPerTag, isPrimary) {
		if (location) {
			this[LOADING_TAGS]++;

			this[loadImages]({
				loadFunction: Load.getLocationImages,
				loadArg: type,
				sourceId: sourceId,
				name: location,
				type: 'location',
				imagesPerTag: imagesPerTag,
				isPrimary: isPrimary,
				icon: LOCATION_ICON,
				extraProps: {
					locationType: type
				}
			});
		}
	}

	[loadDateImages](sourceId, date, imagesPerTag, isPrimary) {
		const self = this;
		const dateString = date.join(DATE_SEPARATOR);
		const end = clone(date);

		const done = () => {
			self[saveImages](sourceId, dateString, 'time', self[CACHE][dateString], imagesPerTag, getExtraProps(isPrimary), DATE_ICON);
		};

		end[end.length - 1] = end[end.length - 1] + 1;

		if (self[CACHE][dateString]) {
			done();
		}
		else {
			Load.getDateImages(date.join(':'), end.join(':'))
				.then((images) => {
					if (Object.keys(images).length <= 1) {
						date.pop();
						if (date.length) {
							self[loadDateImages](sourceId, date, imagesPerTag);
						}
					}
					else {
						self[CACHE][dateString] = images;
						done();
					}
				});
		}
	}

	[loadPersonImages](sourceId, clusterId, imagesPerTag, isPrimary) {
		const self = this;
		const tag = 'Person ' + clusterId;

		const done = () => {
			self[saveImages](sourceId, tag, 'person', self[CACHE][clusterId], imagesPerTag, getExtraProps(isPrimary), PERSON_ICON);
		};

		if (self[CACHE][tag]) {
			done();
		}
		else {
			Load.getPersonImages(clusterId)
				.then((images) => {
					if (!isEmpty(images)) {
						self[CACHE][tag] = images;
						done();
					}
				});
		}
	}

	loadImage(id) {
		const self = this;
		let imagesPerTag = 0;

		const loadRelationships = (data) => new Promise((resolve) => {
			Load.getRelationships(id)
				.then((relationships) => {
					data.relationships = relationships;
					resolve(data);
				});
		});

		const loadNodes = (data) => {
			const people = [];

			self[CACHE].specs[id] = data;

			self[saveImage](data.image_path[0], id, true, {
				gps: data.latitude[0] === -999 ? '-' : data.latitude[0] + ', ' + data.longitude[0],
				datetime: data.datetime[0].indexOf('1970-01-01') === -1 ? data.datetime[0] : '-',
				device: data.model[0] || '-',
				file: data.image_path
			});
			self.onLoad()(clone(self.data));

			self[PEOPLE].forEach((person) => {
				if (person.images.includes(id)) {
					people.push(person.clusterId);
				}
			});

			self[LOADING_TAGS] = data.tag.length + people.length;

			imagesPerTag = clamp(Math.ceil(TARGET_IMAGES / (self[LOADING_TAGS] + 3)), 1, TARGET_IMAGES);

			self[loadLocationImages](id, data.city[0], 'city', imagesPerTag);
			self[loadLocationImages](id, data.state[0], 'state', imagesPerTag);
			self[loadLocationImages](id, data.country[0], 'country', imagesPerTag);

			imagesPerTag = clamp(Math.ceil(TARGET_IMAGES / self[LOADING_TAGS]), 1, TARGET_IMAGES);

			if (isDate(data.datetime, true)) {
				self[LOADING_TAGS]++;

				let date = enforceDate(data.datetime[0], 0, true);
				date = [date.getFullYear(), date.getMonth() + 1, date.getDate()];

				if (!(date[0] === 1970 && date[1] === 1 && date[2] === 1)) {
					self[loadDateImages](id, date, imagesPerTag);
				}
			}

			data.tag.forEach((tag) => self[loadTagImages](id, tag, imagesPerTag));

			people.forEach((clusterId) => self[loadPersonImages](id, clusterId, imagesPerTag));

			data.relationships.forEach((relationship) => self[loadSemanticImages](id, relationship, imagesPerTag));
		};

		self[reset]();

		if (self[CACHE].specs[id]) {
			loadNodes(self[CACHE].specs[id]);
		}
		else {
			Load.getImageSpecs(id)
				.then(loadRelationships)
				.then(loadNodes);
		}
	}

	loadTag(tag) {
		this[reset]()[loadTagImages](null, tag, TARGET_IMAGES, true);
	}

	loadSemantic(words) {
		this[reset]()[loadSemanticImages](null, words, TARGET_IMAGES, true);
	}

	loadLocation(location, locationType) {
		this[reset]()[loadLocationImages](null, location, locationType, TARGET_IMAGES, true);
	}

	loadDate(date) {
		this[reset]()[loadDateImages](null, date.split(DATE_SEPARATOR), TARGET_IMAGES, true);
	}

	loadPerson(clusterId) {
		this[reset]()[loadPersonImages](null, clusterId, TARGET_IMAGES, true);
	}

	query(query, ...args) {
		const self = this;
		query = query.split('~');
		const type = args[0] || query[1];
		query = query[0].replace('_', ' ');
		const queryLower = query.toLocaleLowerCase();
		self.onQuery()();

		if (isNumber(query, true)) {
			self.loadImage(query);
		}
		else if (queryLower.indexOf('person ') === 0 && isNumber(queryLower.replace('person ', ''), true)) {
			self.loadPerson(queryLower.replace('person ', ''));
		}
		else if (self[ALL_TAGS_LOWERCASE].includes(queryLower)) {
			self.loadTag(self[ALL_TAGS][self[ALL_TAGS_LOWERCASE].indexOf(queryLower)]);
		}
		else if (['city', 'state', 'country'].includes(type)) {
			self.loadLocation(query, type);
		}
		else if (type === 'time') {
			self.loadDate(query);
		}
		else {
			let startTag;
			let endTag;

			const isStartTag = self[ALL_TAGS_LOWERCASE].some((tag, index) => {
				startTag = index;
				return queryLower.indexOf(tag) === 0;
			});
			const isEndTag = self[ALL_TAGS_LOWERCASE].some((tag, index) => {
				endTag = index;
				return queryLower.indexOf(tag) + tag.length === queryLower.length;
			});

			if (isStartTag && isEndTag) {
				const predicate = queryLower
					.replace(self[ALL_TAGS_LOWERCASE][startTag], '')
					.replace(self[ALL_TAGS_LOWERCASE][endTag], '')
					.trim();

				self.loadSemantic([self[ALL_TAGS][startTag], predicate, self[ALL_TAGS][endTag]]);
			}
			else {
				console.warn('unknown query: ', query);
			}
		}
	}
};

Object.assign(Load.prototype, {
	onQuery: method.function(),
	onLoad: method.function(),
	onLoadSearch: method.function(),
	onLoadEvents: method.function(),
	onDone: method.function()
});
