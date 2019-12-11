
//http://stackoverflow.com/questions/7641791/javascript-library-for-human-friendly-relative-date-formatting
var general_utils = {
    readableTimeAgo: function(millisec) {
	// Make a fuzzy time
	
	var delta = Math.round((Date.now() - millisec) / 1000);
	
	var minute = 60,
	    hour = minute * 60,
	    day = hour * 24,
	    week = day * 7;

	var fuzzy;

	if (delta < 30) { //SEC
	    fuzzy = 'just then.';
	    
	} else if (delta < minute) { //MINUTES
	    fuzzy = delta + ' seconds ago';
	    
	} else if (delta < 2 * minute) { //MINUTE
	    fuzzy = 'a minute ago';
	    	
	} else if (delta < hour) { //MINUTE
	    fuzzy = Math.floor(delta / minute) + ' minutes ago';
	    
	} else if (Math.floor(delta / hour) == 1) { //HOUER
	    fuzzy = '1 hour ago';
	    	
	} else if (delta < day) { //HOURS
	    fuzzy = Math.floor(delta / hour) + ' hours ago';
	    
	} else if (delta < day * 2) { //DAYS
		var dateMili = new Date(millisec);
		
		var hour = dateMili.getHours();
		var minute = dateMili.getMinutes();
		var second = dateMili.getSeconds();
		var ampm   = (hour >= 12 ? 'pm' : 'am');
		
		hour   = (hour < 10)   ? '0' + hour   : hour;
		minute = (minute < 10) ? '0' + minute : minute;
		second = (second < 10) ? '0' + second : second;
		
	    fuzzy = 'yesterday ' + hour + ":" + minute + ":" + second + ampm;

	} else if (delta < day * 7) { //DAYS
	    fuzzy = Math.floor(delta / day) + ' days ago';

	} else if (delta == day * 7) { //DAYS
	    fuzzy = 'a week ago';

	} else if (Math.floor(delta / week) == 1) { //WEEK
		fuzzy = 'a week ago';
		
	} else {
		fuzzy = new Date(millisec).toDateString();
	}
	
	return fuzzy;
    },

    getProfilePictureUrl: function(facebookId, size) {
        if(!facebookId) {
            console.warn('getProfilePictureUrl incorrect params')
            return;
        }
        var property = "type";
        if(!isNaN(size)) {
            property = "width";
        }
        return "https://graph.facebook.com/" + facebookId + "/picture?" + property + "=" + (size ? size : 'large');
    },

    duplicateObject: function(obj) {
	    return JSON.parse(JSON.stringify(obj));
    },

    objectKeys: function(obj) {
        if (!this.isObject(obj)) {throw new TypeError('_objectKeys called on non-object');}
        var result = [], prop;
        var hasOwnProp = Object.prototype.hasOwnProperty;
        for (prop in obj) { if (hasOwnProp.call(obj, prop)) { result.push(prop); } }
        return result;
    },

    isObject: function(obj) {
        return (obj && obj.constructor === Object);
    },

    isNumeric: function(val) {
	    return !isNaN(+val) && isFinite(val);
	},

    isObjectEmpty: function(obj) {
        if(!this.isObject(obj)) {
            return false;
        }
        for(var prop in obj) {
            if(obj.hasOwnProperty(prop)) {
                return false;
            }
        }
        return JSON.stringify(obj) === JSON.stringify({});
    }
};

export default general_utils;