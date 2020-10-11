var restify = require('restify');
var errors  = require('restify-errors');
var path = require('path');

var BigpipeProcessorManager = require('../BigpipeProcessorManager.js');

var serverToken = undefined;
var processors = {}


function renderError(error) { return new errors.InternalError(error); }
function renderMessage(msg) { return {'message': msg}; }
function handleError(next, error) {
    console.error(error);
    if (error instanceof ReferenceError) {
        return next(new errors.BadRequestError(error.message));
    }
    return next(renderError(error.message));
}

function middlewareValidateRequestToken(req, res, next) {
    var headerToken = req.headers['authorization'].split(' ')[1];
    if(!headerToken || !(serverToken && headerToken == serverToken)) {
        return next(new errors.UnauthorizedError('Unauthorized'));
    }
    next();
}


var server_name = 'bigepipe_node_server';
var server_version = '1.0.0';

const server = restify.createServer({name: server_name, version: server_version});
server.use(restify.plugins.acceptParser(server.acceptable));
server.use(restify.plugins.queryParser({ mapParams: true }));
server.use(restify.plugins.bodyParser({ mapParams: true }));
server.use(restify.plugins.acceptParser(server.acceptable));

var bigpipeProcessorManager = new BigpipeProcessorManager();


server.post('/ding',
            middlewareValidateRequestToken,
            function (req, res, next) {

       res.send(renderMessage('dong, remote server.'));
});

server.post('/register_processor/:processor_name',
            middlewareValidateRequestToken,
            function (req, res, next) {
    bigpipeProcessorManager.registerProcessor(req.params.processor_name, req.files.processor_file.path).then(function() {
        res.send(renderMessage('module [' + req.params.processor_name + '] was registered.'));
    }).catch(function(error) {
        return handleError(next, error);
    });
});

server.post('/process_file/:processor_name',
            middlewareValidateRequestToken,
            function (req, res, next) {
    bigpipeProcessorManager.processFile(req.params.processor_name, req.body.input, req.body.output, req.body.include, req.body.exclude).then(function(effected_files) {
        res.send(effected_files);
    }).catch(function(error) {
        return handleError(next, error);
    });
});

server.post('/render_file/:processor_name',
            middlewareValidateRequestToken,
            function (req, res, next) {

    bigpipeProcessorManager.renderFile(req.params.processor_name, req.body.input, req.body.context, req.body.i18n).then(function(html) {
        res.send(html);
    }).catch(function(error) {
        return handleError(next, error);
    });
});

console.log('BigpipeNodeServer starting')
var BigpipNodeServer = {
    processors: [],
    start: function(port, token, isProduction) {
        server.listen(port, '127.0.0.1', function () {
            serverToken = token;
            bigpipeProcessorManager = new BigpipeProcessorManager(isProduction);
            console.log('%s listening at %s' , server.name, server.url);
        });
    },
}

module.exports = BigpipNodeServer;




