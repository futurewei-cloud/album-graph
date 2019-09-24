import { Container, Drawer, Heading, HEADING_LEVELS, Image, IS_PHONE } from 'hafgufa';
import { castArray, method } from 'type-enforcer';
import { DATE_ICON, LOCATION_ICON, PERSON_ICON, TAG_ICON } from './icons';
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
			ID: 'drawerId',
			dock: 'right',
			width: '16rem',
			closedSize: '2rem',
			isOpen: !IS_PHONE,
			isAnimated: true,
			onOpen: () => {
				this[SELECTION_HEADING_OPEN].isVisible(true);
				this[CONTENT].isVisible(true);
				this[SELECTION_HEADING_CLOSED].isVisible(false);
			},
			onClose: () => {
				this[SELECTION_HEADING_OPEN].isVisible(false);
				this[CONTENT].isVisible(false);
				this[SELECTION_HEADING_CLOSED].isVisible(true);
			},
			content: [
				{
					control: Heading,
					ID: 'selectionHeadingOpen',
					level: HEADING_LEVELS.THREE,
					icon: '',
					title: 'Info',
					margin: '12px',
					buttons: [
						{
							icon: '',
							onClick: () => {
								const newSetting = self[FORCE_GRAPH].highlightNodeType() === 'selected' ? '' : 'selected';
								self[FORCE_GRAPH].highlightNodeType(newSetting);
							}
						}, {
							icon: '',
							onClick: () => self[FORCE_GRAPH].zoom('selected')
						}, {
							icon: '',
							onClick: () => {
								settings.container.get('drawerId').isOpen(false);
							}
						}
					]
				}, {
					control: Container,
					ID: 'contentContainerId',
					padding: '0 16px 16px'
				}, {
					control: Heading,
					ID: 'selectionHeadingClosed',
					level: HEADING_LEVELS.THREE,
					icon: '',
					title: 'Info',
					classes: 'closed-heading',
					isVisible: false,
					onSelect: () => {
						settings.container.get('drawerId').isOpen(true);
					},
					isSelectable: true
				}
			]
		});

		this[SELECTION_HEADING_OPEN] = settings.container.get('selectionHeadingOpen');
		this[SELECTION_HEADING_CLOSED] = settings.container.get('selectionHeadingClosed');
		this[DRAWER] = settings.container.get('drawerId');
		this[CONTENT] = settings.container.get('contentContainerId');

		this.onUnSelect(settings.onUnSelect);
	}
}

Object.assign(SelectionPanel.prototype, {
	selection: method.array({
		set: function(selection) {
			const self = this;
			let content;

			const addMeta = (meta, type, icon, classes) => {
				if (meta[type]) {
					castArray(meta[type]).forEach((title) => {
						content.push({
							control: Heading,
							classes: classes || type,
							isSelectable: true,
							onSelect: function() {
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
				content.push(Object.assign({
					control: Heading,
					level: HEADING_LEVELS.FIVE,
					title: title,
					subTitle: subTitle,
					canWrap: true
				}, extra));
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