---
id: provided_processors
title: Provided Processors
sidebar_label: Provided Processors
---

By default `Bigpipe Response` provide built-in processor to help bundle `javascript`, `node modules/packages`, `React`, `scss`, `i18n` and more...

### jsx 
**type:** `RemoteJsFileProcessor`      
**javascript_handler:** `bigpipe_response.processors.RollupReactProcessor.js`      
**input:** `.jsx/.js` files    
**output:** `.js` file   
**description:**  look for sources files and dependencies 


### js_modules   
**type:** `RemoteJsProcessor`      
**javascript_handler:** `bigpipe_response.processors.WebpackModuleProcessor.js`   
**input:** node packages   
**output:** `.js` file   
**description:** will used to load `js_dependencies` and bundle node modules into a single file.    

For example:        

```python
from bigpipe_response.helpers import to_include

js_react_dependencies = to_include(js_dependencies=['React=react', 'ReactDOM=react-dom', 'Alt=alt', 'createReactClass=create-react-class', 'io=socket.io-client', 'Some=some_lib|abc'], is_link=True, processor_name='js_modules')

return BigpipeResponse(request,
                       render_type=BigpipeResponse.RenderType.TEMPLATE,
                       render_source='main.html',
                       js_dependencies=js_dependencies)
```   

Will result:   
```javascript
React = require('react');     
ReactDOM = require('react-dom');   
Alt = require('alt');    
createReactClass = require('create-react-class');   
io = require('socket.io-client');   
Some = require('some_lib').abc; //Notice how `|` is transleted to `.`
```

  
### css
**type:** `bigpipe_response.processors.css_processor.CSSProcessor`   
**input:** `.scss`    
**output:** `.css`   
**description:** handler writen in python using the `libsass` library


### i18n
type: `bigpipe_response.processors.i18n_processor.I18nProcessor`   
**input:** pay `django` builtin `DjangoTranslation`    
**output:** `.json`   
**description:** using only necessary `django` translation and load them as context.   
