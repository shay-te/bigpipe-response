window.module = {exports: 0};

window.renderI18n = function(i18n) {
    if(typeof django == "object" && typeof django.catalog == "object") {
        for(var key in i18n) { django.catalog[key] = i18n[key]; }
    } else {
        console.error('django jsi18n was never loaded')
    }
}

window.renderPagelet = function(p) {
    try {
        var el = document.getElementById(p.target);
        if (!el) {
            console.error("ERROR: pagelet fill, id:" + p.html + " Not exist");
            return;
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
        if(p.remove) {
            var script = document.getElementById('script_' + p.id);
            if(script) {
                script.parentElement.removeChild(script);
            }
        }
        if(p.i18n) { renderI18n(p.i18n); }
    } catch(err) {
        console.error(err.stack);
    }
};