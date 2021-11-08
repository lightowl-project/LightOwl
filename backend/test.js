let x = "{{bonsoir}} je m'appelle {{ name }}"

const regexp = /{{([\s*a-zA-Z\s*]*)}}/g
const a = [...x.matchAll(regexp)]
console.log(a)


// const string = "{{bonsoir}} je m'appelle {{ name }}"
// const re = /(\B#\w\w+)/g;
// const hits = [];
// // Iterate hits
// let match = null;
// do {
//     match = re.exec(string);
//     if(match) {
//         hits.push(match[0]);
//     }
// } while (match);
// console.log(hits); // Prints [ '#with', '#hashtags' ]