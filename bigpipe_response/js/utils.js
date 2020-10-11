const { Console } = require('console');
var fs = require('fs');
var Stream = require('stream');


var utils = {
    log_ascii: function(obj) {
        var output = '';

        var ws = new Stream;
        ws.writable = true;
        ws.bytes = 0;
        ws.write = function(buf) {
           ws.bytes += buf.length;
           output = buf
        }
        ws.end = function(buf) {
           if(arguments.length) ws.write(buf);
           ws.writable = false;
        }
        const logger = new Console({ stdout: ws, stderr: ws });

        logger.error(obj);
        return output;
    },
}
module.exports = utils;