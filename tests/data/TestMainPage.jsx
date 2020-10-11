import TestSecondPage from './TestSecondPage.jsx';

var TestMainPage = createReactClass({
    getDefaultProps: function() {
        return {props_data: ''};
    },
	render: function () {
		return (
			<html>
				<head>
			        <script type="text/javascript" src="public/javascripts/bigpipe.js"></script>
			        <script type="text/javascript" src="public/javascripts/lib/react.js"></script>
			        <script type="text/javascript" src="public/javascripts/lib/react-dom.js"></script>
			        <script type="text/javascript" src="public/javascripts/lib/alt.js"></script>
				</head>
				<body>
					<div> HERE I AM </div>
					<div id="matches"> </div>
					<div>))){this.props.props_data}(((</div>
					<div>--TRANSLATE--{gettext('CONST_USER_open_question_placeholder_4')}--TRANSLATE--</div>
				</body>
			</html>
		);
	}
});

export default TestMainPage;