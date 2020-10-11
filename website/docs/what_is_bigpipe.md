---
id: what_is_bigpipe
title: What Is Bigpipe
sidebar_label: What Is Bigpipe
---

Bigpipe stream the entire WEB Page content using the singe/initial HTTP connection made by the browser. It divides the WEB page into chunks called pagelets and streams each pagelet content immediately when ready.

By using streaming capabilities we can get access to all assets immediately when they are available from the server. (without loading them using javascript)   
This opens up a way to stream the exact content needed by each pagelet. And stream different content types to each pagelet.

For more information go [here](https://www.facebook.com/notes/facebook-engineering/bigpipe-pipelining-web-pages-for-high-performance/389414033919/) 

# How Bigpipe Works 

##### 1.  The Browser opens an HTTP connection and requests a WEB page.       

##### 2.  The Server will send back the HTML with the following differences:
   
a. `</BODY></HTML>` Tags are emitted.    
Without page closing tags, the browser assumes that the connection is still open and wait for more content.

b. The HTML will be minimal and contain pagelets placeholders.         
Bigpipe will fill the pagelets with content immediately when available.
```html
<html>
    <head>
        <script type="text/javascript" src="public/bigpipe.js"></script>
    </head>
<body>
    ... header
    <div id="pagelet-1"></div>
    <DIV id="pagelet-2"></DIV>
    <DIV id="pagelet-3"></DIV>
    ...
```

c. Tiny javascript file called `bigpipe.js` with a function called `renderPagelet` is included at the top of the page.

##### 3.  The server will process all pagelets simultaneously.
Each pagelet will be processed by a different thread    

##### 4.  Stream pagelet when ready 
The server will wrap each pagelet response into a JSON (this includes JS, CSS, i18n, links, etc...). and stream it back as a javascript function call.
```javascript
<script>
    renderPagelet({
                    "target": "pagelet-1",
                    "css": ".some-class{color:red}....",
                    "js": "function(){.....",
                    "html": "<div class=\"as......",
                    "css_links": ["public/css/x.css", "pu..."],
                    "js_links": ["public/js/y.js", "pu..."],
                  });
</script>
```

##### 5.  the function `renderPagelet` inside the `bigpipe.js` file will pay the JSON data to populate the HTML page.

##### 6.  When all pagelets are served, the server will send closing `</BODY></HTML>` tags. 

##### 7.   The HTTP connection will be closed.
