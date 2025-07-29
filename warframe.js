const { Generator } = require('warframe-name-generator');
const generator = new Generator();
console.log(generator.make({ adjective: true }));