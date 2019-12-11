var simple_js_object = {
    isNumeric: function(val) {
	    return !isNaN(+val) && isFinite(val);
	},
	isY: function() {}
};

//module.exports = function() {return simple_js_object;}();
module.exports = simple_js_object;
