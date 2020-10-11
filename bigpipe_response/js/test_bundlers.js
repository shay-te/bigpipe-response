var fs = require('fs');
var path = require('path');


var React = require('react');
var ReactDOMServer = require('react-dom/server');
var createReactClass = require('create-react-class');


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

//var importFiles = '';
//for(i in include) {
//    importFiles += 'import ' + path.relative(input_file_path, include[i]) + ';\n';
//}

var jsx = require('rollup-plugin-jsx');
var plugins = [ jsx( {factory: 'React.createElement', 'passUnknownTagsToFactory': true} ) ];

var input = 'D:\\programming\\eclipse_projects\\sync_data_python\\conversation\\client\\react\\viewControllers\\ChatViewController.jsx';
//var input = 'D:\\programming\\eclipse_projects\\sync_data_python\\bigpipe\\test\\data\\TestMainPage.jsx';
var output_path = "D:\\programming\\eclipse_projects\\sync_data_python\\bigpipe\\test\\data_output\\component_cache\\jsx\\TestMainPage.jsx.#-#.js";


var includeDependencies= [];
var excludeDependencies = [];
includeDependencies= ['D:\\programming\\eclipse_projects\\sync_data_python\\conversation\\client\\js\\conversation_utils.js'];

//includeDependencies = ["D:\\programming\\eclipse_projects\\sync_data_python\\bigpipe\\test\\data\\simple_js_file.js", "D:\\programming\\eclipse_projects\\sync_data_python\\bigpipe\\test\\data\\folder1\\folder2\\FormLogin.jsx"]
//includeDependencies = ['./folder1/folder2/FormLogin.jsx'];
//includeDependencies = [];
//includeDependencies = {
//    'FormLogin': ["D:\\programming\\eclipse_projects\\sync_data_python\\bigpipe\\test\\data\\folder1\\folder2\\FormLogin.jsx"]
//};



/**
 * ROLLUP
 **/

var build = require('RollupBaseBuild');
build(false, input, output_path, includeDependencies, excludeDependencies, plugins).then(function(effectedFile) {
console.log(effectedFile);
}).catch(function(err) {
    console.error(err);
}) ;


/**
 * BABEL
 **/
//var babelCore = require('@babel/core');
////, '@babel/preset-env'
//var code = fs.readFileSync(input, 'UTF-8');
//var conf = {
//
//    plugins: [
//        "@babel/plugin-transform-runtime",
//          "babel-plugin-inline-import",
//          "@babel/plugin-syntax-dynamic-import",
////        ["transform-runtime", {}]
//    ],
//    presets: [
//        '@babel/preset-react',
////          "@babel/preset-env"
//    ],
////    cwd: path.dirname(input),
//}

//var result =require('@babel/core').transform(code, conf);
//var result =  babelCore.transform(code, conf);
//console.log(result.code);




/**
 * PARCEL
 **/


//var options = {
//    outFile: output_path,
//    watch: false,
//    target: 'browser',
//    autoInstall: false,
//    sourceMaps: false
//}
//const Bundler = require('parcel-bundler');
//const bundler = new Bundler(input, options);
//const bundle =  bundler.bundle();
//
//console.log(bundle.then(function(r) {
//    console.log(r.entryAsset.generated);
//}));














/**
 * WEB PACK
 **/
//
//var webpack = require('webpack');
//var input_arr = includeDependencies.concat([input])
//var relative_out = '../test/data_output/component_cache/jsx/TestMainPage.jsx.#-#.js';//path.relative(input_arr[0], output_path);
//
//const compiler = webpack({
//    entry: input_arr,
//    output: { filename: relative_out},
//    mode: 'development',
//    devtool: false,
//    module: {
//        rules: [
//            {
//                test: /\.jsx$/,
//                exclude: /node_modules/,
//                loader: 'babel-loader',
//                query: {
//                    presets: ["@babel/preset-env", "@babel/preset-react"]
//                },
//            }
//        ]
//    },
//    plugins: [
//
//    ]
//});
//
//
//compiler.run((err, stats) => { // Stats Object
//  // Stats Object
//    console.log("ERROR:");
//  console.log(err);
//  console.log("\n\nSTATS:");
//  console.log(stats);
//});



/**
 * FUSE BOX
 */
//var fusebox = require("fuse-box").fusebox;
//
//var fuse = fusebox({
//  target: 'browser',
//  entry: input,
//  output: output_path,
//  cache : true,
//  devServer: false
//});
//fuse.runProd();


/**
 *resolve-dependencies
 */
//var findImports  = require('find-imports');
//console.log(findImports([input]));