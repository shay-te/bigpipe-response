var fs   = require('fs');
var path = require('path')
var crypto = require('crypto');
var utils = require('./utils.js');

require('register-module')({
  name: 'BaseProcessor',
  path: __dirname,
  main: 'BaseProcessor.js'
});


require('register-module')({
  name: 'RollupBaseBuild',
  path: __dirname,
  main: 'RollupBaseBuild.js'
});


var BaseProcessor = require('BaseProcessor');

class BigpipeProcessorManager {

    constructor(isProduction) {
        this.isProductionMode = isProduction;
        this._processors = {};
    }

    registerProcessor(processor_name, processor_file) {
        console.log('BigpipeProcessorManager.registerProcessor(' + processor_name + ', ...)');
        return new Promise(function(resolve, reject) {
            try {
                this._validateProcessorName(processor_name);
                if(processor_name in this._processors) { reject(new ReferenceError('processor by name [' + processor_name + '] already exists')); }

                this._storeFileLocally(processor_file).then(function(registered_process_file) {
                    var processor_class = require(registered_process_file);
                    if(processor_class.prototype instanceof BaseProcessor) {
                        this._processors[processor_name] = new processor_class(this.isProductionMode);
                        resolve();
                    } else {
                        throw new ReferenceError('process_file must be a type of "BaseProcessor".');
                    }
                }.bind(this)).catch(function(error) {
                    reject(error)
                });
            } catch(error) {
                reject(error)
            }
        }.bind(this));
    }

    processFile(processor_name, inputFile, outputFile, includeDependencies, excludeDependencies) {
        console.log('BigpipeProcessorManager.processFile(' + processor_name + ', ...)');
        return new Promise(function(resolve, reject) {
            try {
                this._validateProcessorName(processor_name);
                this._validateProcessorRegistered(processor_name);

                var promise_result = this._processors[processor_name].processResource(inputFile, outputFile, includeDependencies, excludeDependencies);
                promise_result.then(function(effected_files) {
                    resolve(effected_files);
                }).catch(function(error) {
                    try{
                        var formatted_error = utils.log_ascii(error);
                        reject(new Error(formatted_error));
                    }catch(e) {
                        reject(error);
                    }
                });
            } catch(error) {
                reject(error);
            }
        }.bind(this));
    }

    renderFile(processor_name, inputFile, context, i18n) {
        console.log('BigpipeProcessorManager.renderFile(' + processor_name + ', ...)');
        return new Promise(function(resolve, reject) {
            try {
                this._validateProcessorName(processor_name);
                this._validateProcessorRegistered(processor_name);
                if(!inputFile || !inputFile.trim() || !fs.existsSync(inputFile)) {
                    throw new ReferenceError('render_file must be set and a valid path', inputFile);
                }

                resolve(this._processors[processor_name].renderResource(inputFile, context, i18n));
            } catch(error) {
                reject(error);
            }
        }.bind(this));
    }

    _validateProcessorName(processor_name) {
        if(!processor_name || !processor_name.trim()) { throw new ReferenceError('Processor name cannot be blank'); }
    }

    _validateProcessorRegistered(processor_name) {
        if(!this._processors.hasOwnProperty(processor_name)) { throw new ReferenceError('Processor by name [' + processor_name + '] not registered yet.'); }
    }

    _fileHash(filePath) {
        return new Promise(function(resolve, reject) {
            try {
                let hash = crypto.createHash('md5');
                let stream = fs.ReadStream(filePath)
                stream.on('data', function (data) { hash.update(data); });
                stream.on('end', function () {
                    resolve(hash.digest('hex'));
                });
            } catch (error) {
                return reject(error);
            }
        });
    }

    _storeFileLocally(process_file) {
        return new Promise(function(resolve, reject) {
            if (process_file && fs.existsSync(process_file)) {
                this._fileHash(process_file).then(function(fileHash) {
                    var registered_processors_dir = path.join(__dirname, 'registered_processors');
                    if (!fs.existsSync(registered_processors_dir)){
                       fs.mkdirSync(registered_processors_dir);
                    }
                    var registered_process_file = path.join(registered_processors_dir, fileHash + '.js');
                    if(!fs.existsSync(registered_process_file)) {
                        fs.copyFile(process_file,
                                    registered_process_file,
                                    function(error) {
                                        if (error) { reject(error); }
                                        resolve(registered_process_file);
                                    });
                    } else {
                        resolve(registered_process_file);
                    }

                }).catch(function(error) { reject(error); })
            } else {
                reject(new ReferenceError('process_file must be set and point to a javascript file.'));
            }
        }.bind(this));
    }

}

module.exports = BigpipeProcessorManager;