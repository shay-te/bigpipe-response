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

var bigpipe_node_server = require('./remote_server/bigpipe_node_Server.js');

bigpipe_node_server.start(argv.port, argv.token, modeIndex ? true : false);


