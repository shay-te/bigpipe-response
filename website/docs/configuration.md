---
id: configuration
title: Configuration
sidebar_label: Configuration
---

mandatory fields are marked with `*`
```yaml
bigpipe:
  rendered_output_path: null # * Where to output processed files, this should point to the public directly so files may  
  static_uri: null # * django static dir, needed when processing files a links 
  is_production_mode: null # * true/false. to minify output 
  rendered_output_container: component_cache # inside the public folder where to store rendered files  

  java_script_install_folder: null # absolute path points to node directory. "<temp_folder>/bigpipe_response" isused by default

  remote: # node js remote server
    port_start: 7480 # port number to start scanning for available port
    port_count: 10 # ho many port to scan (remote.port_start + remote.port_count)
    extra_node_packages: [] # install extra node modules. needed when writing plugins

  javascript: # javascript configuration
    default_processor: jsx # default javascript processor is named "jsx"
    bundle_link_dependencies: true # true/false determining if js_dependencies should by bundled or not  
    dom_bind: bigpipe_response.javascript_dom_bind.react_dom_bind.ReactDomBind # what "JavascriptDOMBind" should we use to connect generated Javascript with the DOM

  css: # css configuration
    default_processor: css  
    bundle_link_dependencies: true
    complete_dependencies_by_js: true # true/false. automatically find scss files by the precessed javascript files 

  i18n: # i18n configuration
    default_processor: i18n

  # bigpipe dynamically create and configure processors from this configuration
  # the instances are created using hydra "https://hydra.cc/docs/patterns/objects"
  processors:
    jsx: 
      # create "RemoteJsFileProcessor" named "jsx". and pass the params to the constructor 
      # will use this javascript file "bigpipe_response.processors.RollupReactProcessor.js"
      # will scan for files with the "source_ext" under the "source_paths" 
      # and will convert any resource to the "target_ext" extension.
      class: bigpipe_response.processors.remote_js_file_processor.RemoteJsFileProcessor
      params:
        processor_name: jsx
        javascript_handler: bigpipe_response.processors.RollupReactProcessor.js
        source_paths: null # * list of directories pointing to javascript/react code.
        source_ext:
          - js
          - jsx
        target_ext: js
        exclude_dir: node_modules

    # create "RemoteJsProcessor" named "js_modules". and pass the params to the constructor
    # will use this javascript file "bigpipe_response.processors.WebpackModuleProcessor.js"
    js_modules:
      class: bigpipe_response.processors.remote_js_processor.RemoteJsProcessor
      params:
        processor_name: js_modules
        javascript_handler: bigpipe_response.processors.WebpackModuleProcessor.js
        target_ext: js

    # create "CSSProcessor" named "css". and pass the params to the constructor
    css:
      class: bigpipe_response.processors.css_processor.CSSProcessor
      params:
        processor_name: css
        source_paths: none
        source_ext:
          - scss
        target_ext: css
  
    # create "I18nProcessor" named "i18n". and pass the params to the constructor
    i18n:
      class: bigpipe_response.processors.i18n_processor.I18nProcessor
      params:
        processor_name: i18n
  

```
