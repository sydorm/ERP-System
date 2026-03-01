const fs = require('fs');

const htmlPath = 'g:/Моделювання/R1/calculator-app/frontend/cutter.html';
const cssPath = 'g:/Моделювання/R1/calculator-app/frontend/cutter.css';
const jsPath = 'g:/Моделювання/R1/calculator-app/frontend/cutter.js';

let html = fs.readFileSync(htmlPath, 'utf8');

// Extract CSS
const styleStart = html.indexOf('<style>');
const styleEnd = html.indexOf('</style>', styleStart) + '</style>'.length;
if (styleStart !== -1 && styleEnd !== -1) {
    let css = html.substring(styleStart + '<style>'.length, styleEnd - '</style>'.length);
    fs.writeFileSync(cssPath, css.trim() + '\n', 'utf8');
    html = html.substring(0, styleStart) + '<link rel="stylesheet" href="cutter.css">' + html.substring(styleEnd);
}

// Extract JS
const scriptStart = html.lastIndexOf('<script>');
const scriptEnd = html.lastIndexOf('</script>', scriptStart) + '</script>'.length;
if (scriptStart !== -1 && scriptEnd !== -1) {
    let js = html.substring(scriptStart + '<script>'.length, scriptEnd - '</script>'.length);
    fs.writeFileSync(jsPath, js.trim() + '\n', 'utf8');
    html = html.substring(0, scriptStart) + '<script src="cutter.js"></script>' + html.substring(scriptEnd);
}

fs.writeFileSync(htmlPath, html, 'utf8');
console.log('Split completed successfully.');
