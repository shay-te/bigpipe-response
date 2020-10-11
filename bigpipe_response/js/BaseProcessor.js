var path = require('path');
var fs = require('fs');

class BaseProcessor {
    constructor(isProduction) {
        if (this.constructor == BaseProcessor) { throw new Error("BaseProcessor classes can't be instantiated."); }
        this.fileToModule = {};
        this.isProductionMode = isProduction;
    }

    processResource(mode, inputFile, outputFile, includeDependencies, excludeDependencies) {
        throw new Error("Method 'processResource()' must be implemented.");
    }

    renderResource(renderFile, context, i18n) {
        throw new Error("Method 'renderResource()' must be implemented.");
    }

    _generateBaseModuleSource() {
        var jsi18nPath = path.normalize(path.join(__dirname, 'browser', 'jsi18n.js'));
        return fs.readFileSync(jsi18nPath, 'utf8') + // read django_i18n file
               "global.django = this.django; \n" + // make django_i18n object global
               "Object.getOwnPropertyNames(django).filter(function(property) { if(typeof django[property] == 'function') { global[property] = django[property]; } }); \n"; // move django_i18n methods to be global
    }

    getModuleForFile(render_file, requireAsString) {
        var moduleComponent = this.fileToModule[render_file];
        if(!moduleComponent) {
            var contents = this._generateBaseModuleSource() +
                            requireAsString +
                            fs.readFileSync(render_file, 'utf8');
            var componentsModule  = new module.constructor();
            componentsModule.paths = module.paths;
            componentsModule._compile(contents, path.basename(render_file));
            moduleComponent = componentsModule.exports;

            // Store modules only in production mode
            if(this.isProductionMode) {
                this.fileToModule[render_file] = moduleComponent;
            }
        }
        return moduleComponent;
    }

}

module.exports = BaseProcessor;