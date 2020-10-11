---
id: processors
title: Processors
sidebar_label: Processors
---

Processors are classes that accept any source and transform it into any output supported by the browser.   
by default, BigpipeResponse is providing basic processors for transforming 
* javascript 
* React components 
* scss 
* i18n 

## Processors class diagram.    
<img src="/img/bigpipe.png"/>

### BaseProcessor
The most basic processor object.  
* abstract method `process_resource` that will be called when `render_type=BigpipeResponse.RenderType.JAVASCRIPT` 
* abstract method `render_resource` that will be called when `render_type=BigpipeResponse.RenderType.JAVASCRIPT_RENDER`
* basic validation for source using method `validate_input`
* source, output file name. generated using method `process_source`  
* make sure file will be processed only once

### RemoteJsProcessor(BaseProcessor)
* communicate with remote_js_server 
* register javascript processor to remote js server 
* run javascript processor 

### BaseFileProcessor(BaseProcessor)
* `validate_input` validates the source name format, source file registered and exists. 
* scan for sources by the parameter `source_paths`. 
* store map of files name with no extension to file absolute path
* in development mode will clean processed files after a source file has change

### RemoteJsFileProcessor(BaseFileProcessor)
* process files registered to parent `BaseFileProcessor` 
* communicate with remote_js_server 
* register javascript processor to remote js server 
* run javascript processor 

### CSSProcessor(BaseFileProcessor)
* convert requested scss files to css

### I18nProcessor(BaseProcessor)
* filter django build in catalog and export the filtered keys to a JSON file

