var fs = require('fs');

var file = 'D:\\programming\\eclipse_projects\\sync_data_python\\client\\react\\viewControllers\\ProfilesBoxViewController.jsx';
var acorn = require('acorn');

var defaultAcornOptions = acorn.Options = {
	ecmaVersion: 2020,
	preserveParens: false,
	sourceType: 'module'
};

var result = acorn.Parser.parse(fs.readFileSync(file, 'utf-8'), defaultAcornOptions);
console.log(result);