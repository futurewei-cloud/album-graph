import { delay } from 'async-agent';
import { Container, LocalHistory, theme } from 'hafgufa';
import config from '../graph.config';
import './app.less';
import ForceGraph from './graph/ForceGraph';
import Header from './Header';
import Load from './Load';
import SelectionPanel from './SelectionPanel';

const SMALL_SET_SIZE = 200;
const LARGE_SET_SIZE = 4365;
const CURRENT_SET_SIZE = SMALL_SET_SIZE;

let height = 0;
let width = 0;
let isFirst = true;

theme
	.path('[name].[env].min.css')
	.themes(['moonBeam.dark', 'moonBeam.light'])
	.theme('moonBeam.dark');

const load = new Load(config)
	.onQuery(() => {
		header.isWorking(true);
		isFirst = true;
	})
	.onLoad((data) => {
		forceGraph.data(data)
			.then(() => {
				if (isFirst) {
					delay(() => {
						forceGraph.zoom('selected');
					}, 100);
					isFirst = false;
				}
			});
	})
	.onDone(() => {
		header.isWorking(false);
	})
	.onLoadSearch((suggestions) => {
		header.suggestions(suggestions);
	});

const applyHistory = (historyObject) => load.query(...historyObject);

const history = new LocalHistory({
	onPush: applyHistory,
	onUndo: applyHistory,
	max: 50
});

const loadRandom = () => {
	history.push([Math.round(Math.random() * CURRENT_SET_SIZE).toString()]);
};

const forceGraph = new ForceGraph(Object.assign({
	container: document.body,
	onSelectionChange: (selectedNodes) => {
		selectionPanel.selection(selectedNodes);
	},
	padding: '60 264 40 40',
	onNodeClick: (node) => {
		let query = node.id;
		let extraArg;

		if (node.type === 'location') {
			query = node.label;
			extraArg = node.locationType;
		}
		if (node.type === 'time') {
			extraArg = 'time';
		}

		history.push([query, extraArg]);
	},
	labelExtent: 0,
	labelExtentOnMouseOver: 0,
	singleSelect: true,
	showLabelsOnNodes: true
}, config.graphSettings));

const controlLayer = new Container({
	container: document.body,
	classes: 'control-layer'
});

const header = new Header({
	container: controlLayer,
	title: config.projectName,
	onSearch: (value) => {
		if (value === 'random') {
			loadRandom();
		}
		else if (value === 'undo') {
			history.undo();
		}
		else {
			history.push([value]);
		}
	},
	forceGraph: forceGraph
});

const selectionPanel = new SelectionPanel({
	container: controlLayer,
	forceGraph: forceGraph,
	onUnSelect: (node) => {
		forceGraph.select(node);
	}
});

const updateSize = () => {
	width = Math.floor(window.innerWidth);
	height = Math.floor(window.innerHeight);

	forceGraph
		.height(height)
		.width(width);
};

window.onresize = updateSize;
updateSize();
loadRandom();
