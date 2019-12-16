import { Container, Drawer, Heading, HEADING_LEVELS, Image, IS_PHONE } from 'hafgufa';
import { castArray, method } from 'type-enforcer-ui';
import { DATE_ICON, LOCATION_ICON, PERSON_ICON, SEMANTIC_ICON, TAG_ICON } from './icons';
import './SelectionPanel.less';

const SELECTION_HEADING_OPEN = Symbol();
const SELECTION_HEADING_CLOSED = Symbol();
const DRAWER = Symbol();
const CONTENT = Symbol();
const FORCE_GRAPH = Symbol();

const sorter = (a, b) => {
	if (a.type === b.type) {
		if (a.id === b.id) {
			return 0;
		}
		if (a.id > b.id) {
			return -1;
		}
		return 1;
	}
	if (a.type > b.type) {
		return -1;
	}
	return 1;
};

const getImageFileName = (url) => {
	return url.slice(url.lastIndexOf('filename=') + 9, url.lastIndexOf('&'));
};

export default class SelectionPanel {
	constructor(settings) {
		const self = this;

		self[FORCE_GRAPH] = settings.forceGraph;

		settings.container.append({
			control: Drawer,
			id: 'drawerId',
			dock: 'right',
			width: '16rem',
			closedSize: '2rem',
			isAnimated: true,
			onOpen() {
				self[SELECTION_HEADING_OPEN].isVisible(true);
				self[CONTENT].isVisible(true);
				self[SELECTION_HEADING_CLOSED].isVisible(false);
			},
			onClose() {
				self[SELECTION_HEADING_OPEN].isVisible(false);
				self[CONTENT].isVisible(false);
				self[SELECTION_HEADING_CLOSED].isVisible(true);
			},
			content: [{
				control: Heading,
				id: 'selectionHeadingOpen',
				isVisible: !IS_PHONE,
				level: HEADING_LEVELS.THREE,
				icon: '',
				title: 'Info',
				margin: '12px',
				buttons: [{
					icon: '',
					onClick() {
						settings.container.get('drawerId').isOpen(false);
					}
				}]
			}, {
				control: Container,
				id: 'contentContainerId',
				isVisible: !IS_PHONE,
				padding: '0 16px 16px'
			}, {
				control: Heading,
				id: 'selectionHeadingClosed',
				isVisible: IS_PHONE,
				level: HEADING_LEVELS.THREE,
				icon: '',
				title: 'Info',
				classes: 'closed-heading',
				onSelect() {
					settings.container.get('drawerId').isOpen(true);
				},
				isSelectable: true
			}]
		});

		this[SELECTION_HEADING_OPEN] = settings.container.get('selectionHeadingOpen');
		this[SELECTION_HEADING_CLOSED] = settings.container.get('selectionHeadingClosed');
		this[DRAWER] = settings.container.get('drawerId');
		this[CONTENT] = settings.container.get('contentContainerId');

		this[DRAWER].isOpen(!IS_PHONE);

		this.onUnSelect(settings.onUnSelect);
	}
}

Object.assign(SelectionPanel.prototype, {
	selection: method.array({
		set(selection) {
			const self = this;
			let content;

			const addMeta = (meta, type, icon, classes) => {
				if (meta[type]) {
					castArray(meta[type]).forEach((title) => {
						content.push({
							control: Heading,
							classes: classes || type,
							isSelectable: true,
							onSelect() {
								self[FORCE_GRAPH].zoom('id', title);
								if (IS_PHONE) {
									self[DRAWER].isOpen(false);
								}
							},
							title: title,
							icon: icon
						});
					});
				}
			};

			const addDescription = (title, subTitle, extra = {}) => {
				content.push({
					control: Heading,
					level: HEADING_LEVELS.FIVE,
					title: title,
					subTitle: subTitle,
					canWrap: true,
					...extra
				});
			};

			selection.sort(sorter);

			self[CONTENT].removeContent();

			selection.forEach((node) => {
				content = [];

				if (node.image) {
					content.push({
						control: Image,
						source: node.image.medium,
						width: '100%',
						margin: '0 0 1em'
					});
				}

				if (node.type === 'image') {
					addMeta(node.meta, 'tag', TAG_ICON);
					addMeta(node.meta, 'semantic', SEMANTIC_ICON);
					addMeta(node.meta, 'location', LOCATION_ICON);
					addMeta(node.meta, 'person', PERSON_ICON);
					addMeta(node.meta, 'time', DATE_ICON);

					addDescription('ID:', node.id, {margin: '1em 0 0'});
					addDescription('File:', getImageFileName(node.image.large));
					addDescription('Date:', node.meta.datatime);
					addDescription('GPS:', node.meta.gps);
					addDescription('Device:', node.meta.device);
				}
				else {
					addMeta(node, 'label', node.icon, node.type);
				}

				self[CONTENT].append(content);
			});
		}
	}),
	onUnSelect: method.function()
});
