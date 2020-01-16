---
id: main
title: Intro
sidebar_label: Style Guide
---

# Bigpipe Response


## What is bigpipe response

BigpipeResponse is a standard [django](https://www.djangoproject.com/) `StreamingHttpResponse` response object with the extra capabilities for building fast loading application.   
the project was inspired and using  facebook bigpipe principals. [(BigPipe: Pipelining web pages for high performance)](https://www.facebook.com/notes/facebook-engineering/bigpipe-pipelining-web-pages-for-high-performance/389414033919/)  

### Installing

    pip install bigpipe-response


### Prerequisites

bigpipe response was developed using django version 2.2.4.
make sure you have python `> 3.7` installed
   
### Example project

    https://github.com/shacoshe/bigpipe-response-example


### Basic Configuration
<a name="basic_configuration">
Before getting started we need to tell bigpipe a couple of things.    
`rendered_output_path` point to django public/static directory, bigpipe response will compile assets to a folder under this directory
`processors.jsx.params.code_base_directories` a list folders telling bigpipe where Javascript files are located     
`processors.css.params.code_base_directories` a list folders telling bigpipe where SCSS files are located     
`is_production_mode` boolean indicating if to minify resources and and allow to debug errors in browser   

The following configuration contain only the mandatory options, for more advanced and complete configuration go [here](./configuration.md)    

###### bigpipe_override.yaml
```yaml
bigpipe:
  rendered_output_path: ${full_path:public}
  static_uri: 'public'
  is_production_mode: false

  processors:
    jsx:
      params:
        code_base_directories:
          - ${full_path:client\js}
          - ${full_path:client\react}
    css:
        params:
          code_base_directories:
            - ${full_path:client}
```
</a>

### Initializing 

To start using Bigpipe response just call 
```python
Bigpipe.init(config: DictConfig, processors: list = [])
```


### Loading configuration

`config` parameter in the method `Bigpipe.init(config: DictConfig)` is an [OmegaConf](https://github.com/omry/omegaconf) config object.

#### couple of way to load configuration
##### 1. OmegaConf load the file
```python
config = OmegaConf.load(os.path.join(os.path.dirname(__file__), 'conf', 'bigpipe_response.yaml'))
Bigpipe.init(config.bigpipe)
```
 
The [above configuration](#basic_configuration) is partial config, while `Bigpipe.init` needs the complete configuration file. 

2. Use hydra compose   
1. Use [hydra](https://hydra.cc/) to handle the "main" function. see an example here 

 
 
 
   


### Example Responses

First lets define some react components that we can render back

###### SearchBar.jsx
```javascript
class SearchBar extends React.Component { //ES6
    ....
	render() {
export default SearchBar;
```
###### SearchBarViewController.jsx
```javascript
import SearchBar from '../components/SearchBar/SearchBar.jsx';
import SearchBarActions from '../flux/SearchBarActions.js'
import SearchBarStore from '../flux/SearchBarStore.js'

var SearchBarViewController = createReactClass({  //ES5
    ...
    render: function () { ....
});
export default SearchBarViewController;
```

###### search.html
the HTML fill will have NO closing tags of `</body></htmml>`

```html
<html>
    <head>
        <meta charset="utf-8">
	    <base href="/" target="_blank">
        {% for css_link in css_links %}
            <link rel="stylesheet" media="screen" href="{{css_link}}">
        {% endfor %}
        <script type="text/javascript" src="public/bigpipe.js"></script>
        <script type="text/javascript" src="jsi18n"></script>
        {% for js_link in js_links %}
        <script type="text/javascript" src="{{js_link}}"></script>
        {% endfor %}
    </head>
    <body>
        ...
        <div id="search-bar"> ... </div>
        ....
        <div id="search-results"> ... </div>
        ....
        <div id="chat"> ... </div>
            ....
        <div id="page-bottom"> ... </div>
    ...    
```

###### urls.py
```python
path('', view_search.search, name='search'),
path('search', view_search.search, name='search'),
path('search/<int:last_activity_time>', view_search.search_results, name='Search results'),
path('search_bar', view_search.search_bar, name='search bar'),
```

###### view_search.py
```python
from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.pagelet import Pagelet
from bigpipe_response.helpers import to_include

# javascript dependencies list that will result a javascript bundle file for the modules: react, react-dom, create-react-class
# the dependencies will be available as link to the HTML
# the dependencies will be processed by a processor named "js_modules". 
js_react_dependencies = to_include(['React=react', 'ReactDOM=react-dom', 'createReactClass=create-react-class'], is_link=True, processor_name=Bigpipe.get().config.processors.js_modules.params.processor_name)

@require_GET
def search(request):
    # define what to render and in what section of the HTML to render the result to.
    pagelets = [
        Pagelet(request, 'search-bar', search_bar, {}),
        Pagelet(request, 'search-results', search_results, {'last_activity_time': 0}),
        Pagelet(request, 'chat', view_chat.chat, {}),
        Pagelet(request, 'page-bottom', view_main.page_bottom, {}),  
    ]
    # create a new BigpipeResponse object. that will render the "search.html" using django template engine.
    # will call all pagelets and fill then in the designated position.  
    # will create/load "base_js_function.js" file content and embed it the page HTML page in a designated "<script>" tag
    # will create/load library bundle as load it as a link
    # will create a bindle of javascript by the "main.scss" file
    return BigpipeResponse(request,
                           render_type=BigpipeResponse.RenderType.TEMPLATE,
                           render_source='search.html',
                           render_context={'user_id': request.user.id},
                           pagelets=pagelets,
                           js_dependencies=['base_js_function'] + js_react_dependencies,
                           scss_dependencies=['@main'])

@require_GET
def search_bar(request):
    return BigpipeResponse(request,
                           render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                           render_source='SearchBarViewController',
                           render_context=core_lib.user_search_preference.get_user_search_preference(request.user.id),
                           js_dependencies=['networkLocation'])

@require_GET
def search_profiles(request, last_activity_time):
    return BigpipeResponse(request,
                           render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                           render_source='ProfilesBoxViewController',
                           render_context={'results': core_lib.user_search.search_profiles(request.user.id, None)},
                           js_dependencies=['networkSearch'],
                           i18n_dependencies=["CONST_USER_marital_status.*", "profileboxes_no_more_profiles"])

```
###### view_main.py
```python
@require_GET
def page_bottom(request):
    return BigpipeResponse(request,
                           render_type=BigpipeResponse.RenderType.JAVASCRIPT_RENDER,
                           render_source='PageBottomReactComponent')
```

## What can i do with bigpipe response 

##### 1. Pipelining web pages for high performance
Pipelining web pages allow us to stream all available content and resources back to the browser by using single/initial HTTP connection made to fetch HTML page.

####### pros: 
* no need to wait for javascript code to ajax and fetch data  
* more connection available by the browser for resources 
* no network time for opening more TCP(HTTP) connection [1](https://www.cse.iitk.ac.in/users/dheeraj/cs425/lec14.html)
####### cons: 
* dismisses the browser cache mechanism

##### 2. No Setup Required
There is no need for compiling, preparing, optimizing, uglifiing source files
all is done automatically by response configuration.

##### 3. Fast websites with not effort.
Bigpipe Response is analyzing and building exactly what needed and send it back to the browser.    
this includes `HTML, JavaScript, JavaScript Server Side Rendeing, SASS, i18n. and more`

##### 6. Plug-able 
Use any Javascript framework and more. by creating a custom processor you can easily pipe any source file.  
by default [React](https://reactjs.org/) is supported out of the box.

##### 4. Packing easy control 
Bigpipe Response let you config what resource to load, how to bundle it and how to embed it by telling the response object exactly what you need.  

##### 5. i18n optimization
Bigpipe Response uses django built-in internalization and extends it to be supported by javascript components and server side rendering. 

### Running tests

    python -m unittest discover

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

**Shay Tessler**  - [github](https://github.com/shacoshe)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
  
## examples



## how to extend the existing javascript processor, JAVASCRIPT_DOM_BIND
## how to write a custom processor