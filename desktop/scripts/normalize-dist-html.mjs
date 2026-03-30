import fs from 'node:fs';
import path from 'node:path';

const target = path.resolve('dist/renderer/index.html');

if (!fs.existsSync(target)) {
  console.error(`Missing build output: ${target}`);
  process.exit(1);
}

const original = fs.readFileSync(target, 'utf-8');
const normalized = original
  .replace(/src="\/assets\//g, 'src="./assets/')
  .replace(/href="\/assets\//g, 'href="./assets/');

if (normalized !== original) {
  fs.writeFileSync(target, normalized, 'utf-8');
}

console.log(`Normalized asset paths in ${target}`);
