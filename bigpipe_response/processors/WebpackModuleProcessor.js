var BaseProcessor = require('BaseProcessor');
const VirtualModulePlugin = require('virtual-module-webpack-plugin');
const webpack = require("webpack");
const fs = require('fs');
const path = require('path');

var outputDir = path.resolve(__dirname, 'webpack_assets');
if (!fs.existsSync(outputDir)){
    fs.mkdirSync(outputDir);
}

class WebpackModuleProcessor extends BaseProcessor {

    processResource(input, output, includeDependencies, excludeDependencies) {
        var requireString = '';
        for(var i in includeDependencies) {
            let includeDependency = includeDependencies[i].trim();
            let includeDependencyVariable = undefined;
            if(includeDependency.indexOf('.') > 0) {
                let includeDependencyWithVariable = includeDependency.split('.');
                includeDependency = includeDependencyWithVariable[0];
                includeDependencyVariable = includeDependencyWithVariable[1];
            }
            if(includeDependency.indexOf('=') > 0) {
                let includeSplit = includeDependency.split('=')
                requireString += 'window.'+ includeSplit[0] + ' = require("' + includeSplit[1] + '")'
            } else {
                requireString += 'require("' + includeDependency + '")'
            }
            if(includeDependencyVariable) {
                requireString += '.' + includeDependencyVariable;
            }
            requireString += ';';

        }
        console.log('WebpackModuleProcessor, webpack source: ' + requireString);
        var outputMode = 'development';
        if(this.isProductionMode) { outputMode = 'production' }

        const config = {
            mode: outputMode,
            target: "web",
            entry: { app: "./temp_index.js" },
            output: {
                filename: path.basename(input) + '.js',
                path: path.join(__dirname, 'webpack_assets')
            },
            plugins: [
                new VirtualModulePlugin({
                    moduleName: './temp_index.js',
                    contents: requireString,
                }),
            ],
            module: {
                rules: [
                    {
                        test: /\.script\.js$/,
                        use: [
                            {
                                loader: 'script-loader',
                                options: {
                                    useStrict: false,
                                },
                            },
                        ]
                    }
                ]
            }
        };
        const compiler = webpack(config);
        var result = new Promise(function(resolve, reject) {
            compiler.run(function(err, stats) {
                if(err) {
                    return reject(err);
                }
                var json_stats = stats.toJson();

                if(json_stats.hasOwnProperty('errors') && json_stats.errors.length > 0) {
                    return reject(json_stats.errors);
                }

                var effected_file = [];
                for(var i = 1 ; i < json_stats.modules.length ; i++) {
                    effected_file.push(json_stats.modules[i].identifier);
                }
                const inputFile = path.join(json_stats.outputPath, json_stats.assetsByChunkName.app);
                fs.copyFileSync(inputFile, output);
                resolve(effected_file);
            });
        });

        return result;
    }

    renderResource(render_file, context, i18n) {
        throw new ReferenceError('renderResource Not supported for WebpackModuleProcessor');
    }
}

module.exports = WebpackModuleProcessor;