const rollup = require('rollup');

var path = require('path');
var fs = require('fs');

var uglify = require('rollup-plugin-uglify').uglify;

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
//        resolveId ( source, importer) { return null; },
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
    var input = input_file_path;

    plugins.push(includeFiles(include, exclude))

    if(isProduction) {
        plugins.push(uglify())
    }

    if(extra_plugins && extra_plugins.constructor === Array) {
        plugins = plugins.concat(extra_plugins);
    }

    var inputOptions = {
        input: input_file_path,
        plugins: plugins
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