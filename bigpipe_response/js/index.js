#!/usr/bin/env node
'use strict';

console.log("~");
console.log("~");
console.log("~  ____  _             _                   _____                                      ");
console.log("~ |  _ \\(_)           (_)                 |  __ \\                                     ");
console.log("~ | |_) |_  __ _ _ __  _ _ __   ___  ____ | |__) |___  ___ _ __   ___  _ __  ___  ___ ");
console.log("~ |  _ <| |/ _` | '_ \\| | '_ \\ / _ \\ ____ |  _  // _ \\/ __| '_ \\ / _ \\| '_ \\/ __|/ _ \\");
console.log("~ | |_) | | (_| | |_) | | |_) |  __/      | | \\ \\  __/\\__ \\ |_) | (_) | | | \\__ \\  __/");
console.log("~ |____/|_|\\__, | .__/|_| .__/ \\___|      |_|  \\_\\___||___/ .__/ \\___/|_| |_|___/\\___|");
console.log("~           __/ | |     | |                               | |   ");
console.log("~          |___/|_|     |_|                               |_|");
console.log("~");
console.log("~ Ctrl+C to stop");
console.log("~");


var yargs = require('yargs');

var argv = yargs
    .option('port', {
        alias: 'p',
        description: 'Port to open the server on',
        type: 'number',
    })
    .option('token', {
        alias: 't',
        description: 'security token',
        type: 'string ',
    })
    .option('mode', {
        alias: 'm',
        description: 'development/production mode',
        type: 'string ',
    })
    .help()
    .alias('help', 'h')
    .argv;

if (!argv.port) {
    console.error('port parameter must be set. i.e. --port=800');
    return;
}

if (!argv.token) {
    console.error('token parameter must be set. i.e. --token=alksdjfA(I!@#Z');
    return;
}

if (!argv.mode) {
    console.error('mode parameter must be set. i.e. --mode=DEVELOPMENT/--mode=PRODUCTION');
    return;
}


var modes = ['DEVELOPMENT', 'PRODUCTION'];
var modeIndex = modes.indexOf(argv.mode.toUpperCase())
if(modeIndex == -1) {
    console.error('mode parameter can be values: ' + modes.join(', '));
    return;
}


var bigpipe_node_server = require('./remote_server/bigpipe_node_server.js');
bigpipe_node_server.start(argv.port, argv.token, modeIndex ? true : false);