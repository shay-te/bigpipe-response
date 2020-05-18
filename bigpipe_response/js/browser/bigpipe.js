window.module = {exports: 0};
window.require = function(){};

window.i18n = function(key) {
    if(typeof django == "object" && typeof django.catalog == "object" && django.catalog.hasOwnProperty("key")) {
        return django.catalog[key];
    }
    return key;
}

var _isArr = function(o) {return o && o.constructor === Array;};
window.renderPagelet = function(p) {
    try {
        var el = document.getElementById(p.target);
        if (!el) {
            console.error("ERROR: pagelet fill, id:" + p.html + " Not exist");
            return;
        }
        if(p.i18n) {
            if(typeof django == "object" && typeof django.catalog == "object") {
                for(var key in p.i18n) { django.catalog[key] = p.i18n[key]; }
            } else {
                console.error('django jsi18n was never loaded')
            }
        }
        if(p.html) {
            el.innerHTML = p.html;
        }
        var head=document.getElementsByTagName("head")[0];
        if(p.css) {
            var style  = document.createElement('style');
            style.type = 'text/css';
            if (style.styleSheet){
                  style.styleSheet.cssText = p.css;
            } else {
                  style.appendChild(document.createTextNode(p.css));
            }
            head.appendChild(style);
        }
        if(p.js) {
            var script=document.createElement('script');
            script.type = "text/javascript";
            script.text = p.js;
            head.appendChild(script);
        }
        if(p.js_links && window._isArr(p.js_links)) {
            for(var i in p.js_links) {
                var script = document.createElement("script");
                script.type = "text/javascript"; script.src = p.js_links[i];
                head.appendChild(script);
            }
        }
        if(p.css_links && window._isArr(p.css_links)) {
            for(var i in p.css_links) {
                var link = document.createElement("link");
                link.type = "text/css"; link.rel = "stylesheet"; link.href = p.css_links[i];
                head.appendChild(link);
            }
        }
        if(p.remove) {
            var script = document.getElementById('script_' + p.target);
            if(script) {
                script.parentElement.removeChild(script);
            }
        }
    } catch(err) {
        console.error(err.stack);
    }
};