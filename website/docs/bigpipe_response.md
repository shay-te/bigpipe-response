---
id: bigpipe_response
title: Bigpip Response object
sidebar_label: Bigpip Response object
---

### Bigpipe Response class 

BigpipeResponse object is a standard django 'StreamingHttpResponse' 
```python
class BigpipeResponse(StreamingHttpResponse):
    def __init__(self, request,
                 render_type=RenderType.TEMPLATE,
                 render_source=None,
                 render_context={},
                 pagelets=[],
                 js_dependencies=[],
                 scss_dependencies=[],
                 i18n_dependencies=[],
                 render_options: BigpipeRenderOptions = None):
        ...
```

### Constructor arguments: 
* ##### render_source    
what will be rendered back to the browser.   
the `render_source` can be any resource depends on the `processor` that processes it.  
processors can transform any kind of input, for more information read about  [processors](./processors.md).         

* ##### render_type
    There are 3 types of `render_type` available:   
    `TEMPLATE` call django build in render template with the `render_source`.    
    `JAVASCRIPT` call the default/specific processor.      
    `JAVASCRIPT_RENDER` server side render on the default/specific processor. 
* ##### render_context `(dict)`
    when `render_type` is `TEMPLATE` it willl act as `context` for django template engine.    
    when `render_type` is `JAVASCRIPT`/`JAVASCRIPT_RENDER`. act as `React props` in case of default processor.
* ##### js_dependencies
    list of string indicating what additional `javascript` files are loaded in `<script>` tag or as a `link`       
    for more info see  [js/css dependencies string format](#js_css-dependencies-string-format)      
* ##### css_dependencies
    list of string indicating what additional `css` files are loaded in the `<style>` tag or as a `link`       
    for more info see  [js/css dependencies string format](#js_css-dependencies-string-format)      
* ##### i18n_dependencies
    list of regular expression string filtering django internalization strings and making them available for the client. 
* ##### render_options (`BigpipeRenderOptions`)
    `js_processor_name` the processor name to process the `render_source` and `js_dependencies`.   
    `css_processor_name` the processor name to process the `css_dependencies`.   
    `i18n_processor_name` the processor name to process the `i18n_dependencies`.   
    `js_bundle_link_dependencies` should javascript link resources should be bundled or independent    
    `css_bundle_link_dependencies` should css link resources should be bundled or independent
    `css_complete_dependencies_by_js` should include css files with the same name of javascript resources.   
    `js_dom_bind` what is the `JavascriptDOMBind` that will link the `javascript` to the `HTML`.

    


### js/css dependencies string format
<a name="js_css-dependencies-string-format"></a>

the format of the dependencies is a list of filenames without the extension in the following format `<@><processor_name>:<resource_name>`   

1. `@` when available the file will be served as a link
2. `<processor_name>:` the processor name the will process the resource
3. `<resource_name>` the resource name (file name without extension.)


for example:   
* `js_processor_name=['file_1', 'file2']` :   
will process `file_1` and `file_2` with the default javascript processor.

* `js_processor_name=['js_2:file_1', 'file2']`      
will process `file_1` with a processor named `js_2` and `file_2` with the default javascript processor
 
* `css_processor_name=['css_2:file_1', 'file2']`    
will process `file_1` with a processor named `css_2` and `file_2` with the default css processor

* `js_processor_name=['@file_1', 'file2']`
will process `file_1` and `file_2` with the default javascript processor. while `file_1` will be available as a link at the `render_context`


* `['js_module:React=react']`
will process `React=react` with a processor named `js_module`. while `js_module` is a custom processor the builds a require string for webpack. 
for example 

in order to build include string more easily we can pay the function `bigpipe_response.helpers.to_include` that will build the dependencies list for us.     
for example: 
`to_include(['React=react', 'ReactDOM=react-dom'], is_link=True, processor_name=Bigpipe.get().config.processors.js_modules.name)`         
will result: `['@js_module:React=react', '@ReactDOM=react-dom']`
    
 
