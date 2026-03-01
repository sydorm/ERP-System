const fs = require('fs');
const { execSync } = require('child_process');

try {
    console.log('Restoring cutter.html to last commit...');
    execSync('git restore cutter.html', { cwd: 'g:/Моделювання/R1/calculator-app/frontend' });
    console.log('Restore successful.');
} catch (e) {
    console.error('Git restore failed, falling back to git checkout', e.message);
    try {
        execSync('git checkout -- cutter.html', { cwd: 'g:/Моделювання/R1/calculator-app/frontend' });
    } catch (e2) {
        console.error('Git checkout also failed. Please manually git restore cutter.html');
        process.exit(1);
    }
}

const htmlPath = 'g:/Моделювання/R1/calculator-app/frontend/cutter.html';
const cssPath = 'g:/Моделювання/R1/calculator-app/frontend/cutter.css';
const jsPath = 'g:/Моделювання/R1/calculator-app/frontend/cutter.js';

let html = fs.readFileSync(htmlPath, 'utf8');

// 1. Extract CSS
const styleStartTag = '<style>';
const styleEndTag = '</style>';
const styleStart = html.indexOf(styleStartTag);
const styleEnd = html.indexOf(styleEndTag, styleStart);

if (styleStart !== -1 && styleEnd !== -1) {
    const css = html.substring(styleStart + styleStartTag.length, styleEnd);
    fs.writeFileSync(cssPath, css.trim() + '\n', 'utf8');
    html = html.substring(0, styleStart) + '<link rel="stylesheet" href="cutter.css">' + html.substring(styleEnd + styleEndTag.length);
}

// 2. Extract JS
const scriptStartTag = '<script>';
const scriptEndTag = '</script>';
const scriptStart = html.lastIndexOf(scriptStartTag);
const scriptEnd = html.lastIndexOf(scriptEndTag); // this works because script is at the end of the file

if (scriptStart !== -1 && scriptEnd !== -1 && scriptEnd > scriptStart) {
    const js = html.substring(scriptStart + scriptStartTag.length, scriptEnd);
    fs.writeFileSync(jsPath, js.trim() + '\n', 'utf8');
    html = html.substring(0, scriptStart) + '<script src="cutter.js"></script>' + html.substring(scriptEnd + scriptEndTag.length);
}

fs.writeFileSync(htmlPath, html, 'utf8');
console.log('Split completed successfully! Please check cutter.html, cutter.css, and cutter.js.');
