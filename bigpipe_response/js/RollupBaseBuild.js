const rollup = require('rollup');

var path = require('path');
var fs = require('fs');

var terser = require('rollup-plugin-terser').terser;
var resolve = require('@rollup/plugin-node-resolve').nodeResolve;
var commonjs = require('@rollup/plugin-commonjs');
var injectProcessEnv = require('rollup-plugin-inject-process-env');



function includeFiles (include, exclude) {
    const emptyFile = 'export default {}';
    const emptyFileName = '\0empty_module';
    var loadCalled = true;
    if(include.length > 0) {
        var importFiles = '';
        loadCalled = false;
        for(i in include) {
            importFiles += 'import \'' + include[i].replace(/\\/g, '/') + '\';\n';
        }
    }
    return {
        name: 'include-files',
        load ( id ) {
            if(!loadCalled) {
                loadCalled = true;
                return importFiles + fs.readFileSync(id, 'utf-8');;
            }
            return null;
        }
    };
}

async function build(isProduction, input_file_path, output_file_path, include, exclude, extra_plugins) {
    var plugins = [];
    plugins.push(injectProcessEnv({NODE_ENV: isProduction ? 'production' : 'development'}));
    plugins.push(resolve({browser: true, jsnext: true}));
    plugins.push(commonjs({include: '/node_modules/'}));
    plugins.push(includeFiles(include, exclude))
    if(extra_plugins && extra_plugins.constructor === Array) {
        plugins = plugins.concat(extra_plugins);
    }

    if(isProduction) {
        plugins.push(terser({
                                ecma: 5,
                                mangle : false,
                                keep_classnames: true,
                                keep_fnames: true,
                                compress: {
                                    reduce_vars: false,
                                    unused: false
                                }
                            }));
    }

    var inputOptions = {
        input: input_file_path,
        plugins: plugins,
        context: 'window'
    }

    var outputOptions = {
        file: output_file_path,
        format: 'cjs'
    };

    const bundle = await rollup.rollup(inputOptions);

    const { output } = await bundle.generate(outputOptions);

    await bundle.write(outputOptions);

    return bundle.watchFiles;
}

module.exports = build;