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
            requireString += 'require("' + includeDependencies[i] + '"); \n'
        }

        var outputMode = 'development';
        if(this.isProductionMode) { outputMode = 'production' }

        const config = {
            mode: outputMode,
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
        };
        const compiler = webpack(config);
        var res, rej;
        var result = new Promise(function(resolve, reject) {
            res = resolve;
            rej = reject;
        });

        compiler.run(function(err, stats) {
            if(err) {
                return rej(err);
            }
            var json_stats = stats.toJson();

            var effected_file = [];
            for(var i = 1 ; i < json_stats.modules.length ; i++) {
                effected_file.push(json_stats.modules[i].identifier);
            }

            const inputFile = path.join(json_stats.outputPath, json_stats.assetsByChunkName.app);
            fs.copyFileSync(inputFile, output);

            res(effected_file);
        });

        return result;
    }

    renderResource(render_file, context, i18n) {
        throw new ReferenceError('renderResource Not supported for WebpackModuleProcessor');
    }
}

module.exports = WebpackModuleProcessor;