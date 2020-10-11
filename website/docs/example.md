---
id: example
title: Example
sidebar_label: Example
---


### Basic Configuration
<a name="basic_configuration"></a>

Before getting started we need to tell bigpipe a couple of things.    
`rendered_output_path` point to django public/static directory, bigpipe response will compile assets to a folder under this directory   
`processors.jsx.params.source_paths` a list of folders telling bigpipe where Javascript files are located         
`processors.css.params.source_paths` a list of folders telling bigpipe where SCSS files are located         
`is_production_mode` boolean indicating if to minify resources and allow to debug errors in the browser   

The following configuration contains only the mandatory options, for more advanced and complete configuration, go [here](./configuration.md)    

###### bigpipe_override.yaml
```yaml
bigpipe:
  rendered_output_path: ${full_path:public}
  static_uri: 'public'
  is_production_mode: false

  processors:
    jsx:
      params:
        source_paths:
          - ${full_path:client\js}
          - ${full_path:client\react}
    css:
        params:
          source_paths:
            - ${full_path:client}
```

### Loading configuration

`config` parameter in the method `Bigpipe.init(config: DictConfig)` is an [OmegaConf](https://github.com/omry/omegaconf) config object.

#### couple of way to load configuration
##### 1. OmegaConf load the file
```python
import os
from omegaconf import OmegaConf
from bigpipe_response.bigpipe import Bigpipe

project_path = os.path.dirname(__file__)
OmegaConf.register_resolver('full_path', lambda sub_path: os.path.join(project_path, sub_path))
config = OmegaConf.load(os.path.join(project_path, 'conf', 'bigpipe_response.yaml'))
Bigpipe.init(config.bigpipe)
```
 
The [above configuration](#basic_configuration) is partial config, while `Bigpipe.init` needs the complete configuration file. 

##### 2. Leverage [hydra](https://hydra.cc/) to configure the entire application.
###### bigpipe_override.yaml
```yaml
defaults:
  - bigpipe
  - bigpipe_override

django:
  port: 8080
  params:
    - runserver
    - ${django.port}

core_lib:
  db:
    protocol: mysql
    username: test
    password: test
    host: localhost
    port: 3306
    file: test

hydra: # tell hydra to pay the same output directory
  run:
    dir: outputs
``` 

###### < your django app >/manage.py
```python
@hydra.main(config_path="../config/app_config.yaml")
def main(cfg):
   ...
    if os.environ.get('RUN_MAIN') == 'true':
        OmegaConf.register_resolver('full_path', lambda sub_path: os.path.join(project_path, sub_path))
        from bigpipe_response.bigpipe import Bigpipe
        Bigpipe.init(cfg.bigpipe)  # Setup bigpipe
        CoreLib(cfg.demo)  # Setup app instance
    ...
    execute_from_command_line(setup_django_params(cfg))


def setup_django_params(cfg):  # sys.argv is a list of string, django expect port to be a string.
    result = [str(cfg.django.params[i]) for i in range(len(cfg.django.params))]
    result.insert(0, __file__)  # set manage.py
    return result

def handle_kill(signum, frame):
    print('Signal terminate received will shutdown bigpipe')
    from bigpipe_response.bigpipe import Bigpipe
    Bigpipe.get().shutdown()

if __name__ == '__main__':
    signal.signal(signal.SIGTERM , handle_kill)
    signal.signal(signal.SIGINT, handle_kill)
    main()      
```   


### Initializing 

To start using Bigpipe response just call 
```python
Bigpipe.init(config: DictConfig, processors: list = [])
```
 
### Example Responses

First lets define some react components that we can render back

###### SearchBar.jsx
```javascript
class SearchBar extends React.Component { //ES6
   render() {
    ....
export default SearchBar;
```
###### SearchBarViewController.jsx
```javascript
import SearchBar from '../components/SearchBar/SearchBar.jsx';
import SearchBarActions from '../flux/SearchBarActions.js'
import SearchBarStore from '../flux/SearchBarStore.js'

var SearchBarViewController = createReactClass({  //ES5
    ...
    render: function () { 
    ....
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

* javascript dependencies list that will result in a javascript bundle file for the modules: `react`, `react-dom`, `create-react-class`
* the dependencies will be available as a link to the HTML
* the dependencies will be processed by a processor named `js_modules`. 

```python
from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.pagelet import Pagelet
from bigpipe_response.helpers import to_include

js_react_dependencies = to_include(['React=react', 'ReactDOM=react-dom', 'createReactClass=create-react-class'], is_link=True, processor_name=Bigpipe.get().config.processors.js_modules.params.processor_name)
```

* `BigpipeResponse.RenderType.TEMPLATE` renders `search.html` using django template engine.       
* Bundle `base_js_function.js` plus dependencies and embed it as a designated `<script>` tag.        
* Bundle `js_react_dependencies` plus dependencies and pass it as link to the render_context      
* Bundle `main.scss` plus dependencies and pass it as link to the render_context      
* Template context `{'user_id': request.user.id, 'css_link': ['/public/<css bundle files>'], 'js_link': ['/public/<js bundle files>']}`
* Define pagelets to fill designated DOM elements (after serving `search.html`).

```python
@require_GET
def search(request):
    # define what to render and in what section of the HTML to render the result to.
    pagelets = [
        Pagelet(request, 'search-bar', search_bar, {}),
        Pagelet(request, 'search-results', search_results, {'last_activity_time': 0}),
        Pagelet(request, 'chat', view_chat.chat, {}),
        Pagelet(request, 'page-bottom', view_main.page_bottom, {}),  
    ]
    return BigpipeResponse(request,
                           render_type=BigpipeResponse.RenderType.TEMPLATE,
                           render_source='search.html',
                           render_context={'user_id': request.user.id},
                           js_dependencies=['base_js_function'] + js_react_dependencies,
                           scss_dependencies=['@main'], 
                           pagelets=pagelets,)
```

* `BigpipeResponse.RenderType.JAVASCRIPT` renders `SearchBarViewController.jsx` 
* include `networkLocation.js` and add to the javascript dependencies.
* Use `ReactDomBind` to bind `SearchBarViewController` React component to the DOM
* `render_context` will be used ad the "props" for the `SearchBarViewController` component 
* embed javascript content into HTML page in a designated `<script>` tag

```python
@require_GET
def search_bar(request):
    return BigpipeResponse(request,
                           render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                           render_source='SearchBarViewController',
                           render_context=core_lib.user_search_pref.get_by_user_id(request.user.id),
                           js_dependencies=['networkLocation'])
```

* `BigpipeResponse.RenderType.JAVASCRIPT` will lookup for `ProfilesBoxViewController.jsx`
* include `networkSearch.js` and add to the javascript dependencies.
* Use `ReactDomBind` to bind `ProfilesBoxViewController` React component to the DOM
* `render_context` will be used ad the `props` for the `SearchBarViewController` component 
* embed javascript content into HTML page in a designated `<script>` tag
* generate a i18n json and append it to the `render_context` 

```python
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

* `BigpipeResponse.RenderType.JAVASCRIPT_RENDER` will lookup for `PageBottomReactComponent.jsx`.
* pass `context` as react props. 
* server side render `PageBottomReactComponent` with `context` as props. 

```python
@require_GET
def page_bottom(request):
    context = {...}
    return BigpipeResponse(request,
                           render_type=BigpipeResponse.RenderType.JAVASCRIPT_RENDER,
                           render_context=context,
                           render_source='PageBottomReactComponent')
```

