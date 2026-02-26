#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const CSS_SOURCE = '/Volumes/The Secret Archive/02_PROJECTS/Web_Development/css-themes-styles';
const OUTPUT = path.join(__dirname, '../assets/abd-themes.css');

const THEME_ORDER = [
  'ca-assembly-daily-file.css',
  'cable-news.css',
  'california-dreaming.css',
  'california-mission.css',
  'cubism.css',
  'disco.css',
  'france.css',
  'free-love.css',
  'highway-street-photo.css',
  'impressionist.css',
  'italy.css',
  "american-wave.css",
  'military-theme.css',
  'millennial-myspace.css',
  'national-parks-poster.css',
  'newspaper.css',
  'nineties-graphic-design.css',
  'renaissance.css',
  'retro-diner.css',
  'retro-internet.css',
  'retro-tech-polaroid.css',
  'stars-and-stripes.css',
  'stpatricks.css',
  'las-vegas.css',
  'travel-nyc-liberty.css',
  'pink-yellow.css',
  'wayfinding-receipt.css',
  'zine.css'
];

let output = '/* Auto-generated ABD Themes - Do not edit directly */\n\n';

for (const file of THEME_ORDER) {
  const srcPath = path.join(CSS_SOURCE, file);
  if (!fs.existsSync(srcPath)) {
    console.warn('Missing:', file);
    continue;
  }
  const content = fs.readFileSync(srcPath, 'utf8');
  const baseName = file.replace('.css', '');
  output += `/* --- ${file} --- */\n${content}\n\n`;
}

fs.writeFileSync(OUTPUT, output);
console.log('Built abd-themes.css from', THEME_ORDER.length, 'theme files');
