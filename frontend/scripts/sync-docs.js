import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const APP_ROOT = path.resolve(__dirname, '../../');
const DOCS_SRC = path.join(APP_ROOT, 'docs', 'documentation creation task');
const SCREENSHOTS_SRC = path.join(APP_ROOT, 'docs', 'documentation creation task screenshots');

const FRONTEND_PUBLIC_DOCS = path.join(APP_ROOT, 'frontend', 'public', 'docs');
const DOCS_DEST = path.join(FRONTEND_PUBLIC_DOCS, 'content');
const SCREENSHOTS_DEST = path.join(FRONTEND_PUBLIC_DOCS, 'screenshots');

function copyDirectorySync(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  if (!fs.existsSync(src)) return;

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (let entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirectorySync(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// Clean target directory
if (fs.existsSync(FRONTEND_PUBLIC_DOCS)) {
  fs.rmSync(FRONTEND_PUBLIC_DOCS, { recursive: true, force: true });
}

console.log('Copying documentation...');
copyDirectorySync(DOCS_SRC, DOCS_DEST);

console.log('Copying screenshots...');
copyDirectorySync(SCREENSHOTS_SRC, SCREENSHOTS_DEST);

console.log('Done syncing docs!');
