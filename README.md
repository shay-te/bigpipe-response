# Bigpipe Response

a bigpipe response for django


## What is bigpipe response

Bigpipe Response is a django response object for building fast loading application    
by using the principals of [facebook bigpipe](https://www.facebook.com/notes/facebook-engineering/bigpipe-pipelining-web-pages-for-high-performance/389414033919/)
(BigPipe: Pipelining web pages for high performance)  
it boosts web site performance by:
 1. Loading exactly whats needed for the page to work (HTML,JS,CSS,i18n)
 2. Pipelining web pages using the single http connection to load all resources. (this dismisses the browser cache mechanism)      

#### Bigpipe Response give the following advantages:

##### 1. No Setup Required.
There is no need for compiling, preparing, optimizing, uglifiing source files    
all is done automatically by response configuration.

##### 2. Fast websites with not effort.    
Bigpipe Response loads exactly whats needed. 
* HTML
* JavaScript
* Server side rendered JavaScript 
* SASS
* i18n.

##### 3. Pipelining web pages for high performance.    
Response data is streamed once available using the original HTTP connection.         

##### 4. Use any Javascript framework.
Bigpipe Response is plug-able, you can easily pipe any source file (react/angular/other)   

##### 5. Complex bundling tasks with no effort.
Bigpipe Response let you config what to load and how to embed it.

##### 6. i18n optimization
Bigpipe Response uses django build in internalization 
      

### Prerequisites

bigpipe response was developed using django version 2.2.4. 
and using [omegaconf](https://github.com/omry/omegaconf) for configuration 

### Installing

    pip install bigpipe_response


## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

**Shay Tessler**  - [github](https://github.com/shacoshe)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
