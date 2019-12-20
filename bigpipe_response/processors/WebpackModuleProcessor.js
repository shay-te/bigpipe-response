const fs = require('fs');

class WebpackModuleProcessor extends BaseProcessor {

    processResource(input, output, includeDependencies, excludeDependencies) {
        var requireString = '';
        for(var i in includeDependencies) {
            requireString += 'require("' + includeDependencies[i] + '""); \n'
        }
        var outputMode = 'development';
        if(this.isProductionMode) { outputMode = 'production' }

        const config = {
            mode: outputMode,
            entry: { app: "./temp_index.js" },
            output: { filename: 'out.js' },
            plugins: [
                new VirtualModulePlugin({
                    moduleName: './temp_index.js',
                    contents: requireString,
                }),
            ],
        };
        const compiler = webpack(config);
        compiler.run(function(err, stats) {
            if(err) { throw err; }
            const outfile = path.join(__dirname, stats.toJson().assetsByChunkName.app);
            fs.copyFileSync("filepath1", "filepath2");
        })
    }

    renderResource(render_file, context, i18n) {
        throw new ReferenceError('renderResource Not supported for WebpackModuleProcessor');
    }
}

module.exports = WebpackModuleProcessor;