---
id: main
title: Getting started
sidebar_label: Getting started
---

# What is Bigpipe Response

BigpipeResponse is a standard [django](https://www.djangoproject.com/) `StreamingHttpResponse` response object with the extra capabilities for building and fast loading application.   
the project was inspired and using facebook bigpipe principals. [(BigPipe: Pipelining web pages for high performance)](https://www.facebook.com/notes/facebook-engineering/bigpipe-pipelining-web-pages-for-high-performance/389414033919/)  

## Installing

    pip install bigpipe-response

## Prerequisites

    `django > 2.2.4`, `python > 3.7`

## Running tests

    python -m unittest discover


## The source

[https://github.com/shacoshe/bigpipe-response](https://github.com/shacoshe/bigpipe-response)
   
## Example project

[https://github.com/shacoshe/bigpipe-response-example](https://github.com/shacoshe/bigpipe-response-example)

## Pros:    
* no need to wait for javascript code to ajax and fetch data/code  
* more connection available by the browser for resources 
* no network time for opening more TCP/HTTP connections [1](https://www.cse.iitk.ac.in/users/dheeraj/cs425/lec14.html)

## Cons:    
* dismisses the browser cache mechanism for embedded results

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

**Shay Tessler**  - [github](https://github.com/shacoshe)


## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE.md](LICENSE) file for details

