---
id: custom_processors
title: Custom Processors
sidebar_label: Custom Processors
---

# Custom Processors

Bigpipe Response gives a couple of options for extending processing functionality. 

by implementing `BaseProcessor` methods

```python

def process_resource(self, source: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
   pass

def render_resource(self, source: str, context: dict, i18n: dict):
   pass

```



### 1. Custom python processor 
By extending `BaseProcessor` or `BaseFileProcessor` for file scanning functionality, we can create any processor that we like. 

For example markdown processor:

```python
from pathlib import Path

from bigpipe_response.processors.base_file_processor import BaseFileProcessor
import markdown2

class MarkdownProcessor(BaseFileProcessor):

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        fp = open(output_file, "w", encoding='utf-8')
        fp.write(self.__from_input(input_file))
        fp.close()

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return self.__from_input(input_file)

    def __from_input(self, input_file):
        return markdown2.markdown(Path(input_file).read_text(), extras=[])
```



### 2. Custom Javascript Processor  

By creating a javascript class that extends the javascript `BaseProcessor`. we can create any javascript processor.  


```javascript
var BaseProcessor = require('BaseProcessor');
var build = require('RollupBaseBuild');
var jsx = require('rollup-plugin-jsx');

var VuePlugin = require('rollup-plugin-vue');
var plugins = [ VuePlugin() ];

class VueProcessor extends BaseProcessor {

    processResource(input, output, includeDependencies, excludeDependencies) {
        if(input && output) {
            return build(this.isProductionMode, input, output, includeDependencies, excludeDependencies, plugins);
        } else {
            throw new ReferenceError('input, output parameters are require to process the file', input);
        }
    }

    renderResource(render_file, context, i18n) {
        throw new ReferenceError('NOT SUPPORTED');
    }

}

module.exports = VueProcessor;
```

after creating the javascript processor we can describe it's package position in the `javascript_handler` property of the `RemoteJsProcessor`/`RemoteJsFileProcessor` constructor.

in the example above we are using, `var build = require('RollupBaseBuild');`  this will give us a basic [rollupjs](http://rollupjs.org/guide/en/) build function that accepts a list of plugins as the last argument. 

# Registering New Processors 

Bigpipe Response provides two ways to register processors 

### 1. config.yaml
the base `bigpipe_response.yaml` config file list all default processors.  
when calling the `Bigpipe.init(config)`. Bigpipe will register all processors under the `bigpipe.processors` path.  
by overriding the default configuration we can add new processor or edit existing processors 
for example a defining a new javascript processor : 

```yaml
bigpipe:
  processors:
    my_new_processor:
      class: bigpipe_response.processors.remote_js_processor.RemoteJsProcessor
      params:
        processor_name: my_new_processor
        javascript_handler: mypackage.MyProcessor.js
        target_ext: js
```

### 2. Bigpipe Initialization   
When calling `Bigipe.init()` the second parameter is a list of `BaseProcessor` instances.   
processors here will override processors introduced in the `config.yaml` with the same `processor_name`.
```python
custom_processors = [MyProcessor(), 
                     MarkdownProcessor('markdown_proc', ['/some/dir/path'], ['htm', 'html'], 'html'), 
                     RemoteJsProcessor('my_new_processor, 'pkg1.pkg2.MyJavascriptHandlder.js', 'js')]
Bigipe.init(config, custom_processors)
```



# Deep Understanding 

for more deeply understand how `BaseProcessor` works. please take a look at the comments on the [code here](https://github.com/shay-te/bigpipe-response/blob/master/bigpipe_response/processors/base_processor.py)

