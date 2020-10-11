var simple_js_object = {
    isNumeric: function(val) {
	    return !isNaN(+val) && isFinite(val);
	},
	function_inside_simple_js_object: function() {},
	isY: function() {}
};

//module.exports = function() {return simple_js_object;}();
module.exports = simple_js_object;
//export default simple_js_object;
