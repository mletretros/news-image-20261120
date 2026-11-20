// The World Today is a newspaper front page for Friday 20 November 2026.
// generate.py drew this world-news briefing with Pillow and its custom icons.
// This entrypoint validates the finished PNG before carrying it to the judge.
// The final artifact is copied to /output/entry.png for the make.fun news-image judge.

import { copyFileSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const source = new URL('./entry.png', import.meta.url);
const png = readFileSync(source);
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);

if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png must be 1024x1024; received ${width}x${height}`);
}
if (png.length > 1048576) {
  throw new Error('entry.png exceeds the 1048576-byte limit');
}

copyFileSync(source, join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
