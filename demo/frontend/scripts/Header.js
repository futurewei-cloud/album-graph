import { Button, Container, Header, Heading, HEADING_LEVELS, SearchBar } from 'hafgufa';
import config from '../graph.config';
import './Header.less';

const IS_WORKING = Symbol();
const SEARCH_BAR = Symbol();

export default class {
	constructor(settings) {
		settings.container.append({
			control: Container,
			content: [
				{
					control: Header,
					id: 'isWorkingId',
					isWorkingLabel: 'Loading',
					content: [
						{
							control: Heading,
							level: HEADING_LEVELS.ONE,
							title: config.projectName || 'title'
						}, {
							control: Container,
							classes: 'align-right',
							content: [
								{
									control: Button,
									classes: 'header-button',
									icon: '',
									label: 'Fit',
									onClick() {
										return settings.forceGraph.zoom('fit');
									}
								}, {
									control: Button,
									classes: 'header-button',
									icon: '',
									alt: 'Random',
									onClick() {
										return settings.onSearch('random');
									}
								}, {
									control: Button,
									classes: 'header-button',
									icon: '',
									alt: 'Undo',
									onClick() {
										return settings.onSearch('undo');
									}
								}, {
									control: SearchBar,
									id: 'searchBar',
									breakOnSpaces: false,
									isCompact: true,
									localizedStrings: {
										search: 'Search'
									},
									onChange(value) {
										if (value[0]) {
											settings.onSearch(value[0]);
										}
									}
								}
							]
						}
					]
				}
			]
		});

		this[IS_WORKING] = settings.container.get('isWorkingId');
		this[SEARCH_BAR] = settings.container.get('searchBar');
	}

	isWorking(isWorking) {
		this[IS_WORKING].isWorking(isWorking);
	}

	suggestions(suggestions) {
		this[SEARCH_BAR].suggestions(suggestions);
	}
}
