import { execFileSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';

const EXPECTED_VERSION = '0.39.1';
const EXPECTED_RPC = 'https://studio.genlayer.com/api';
const EXPECTED_CHAIN = '61999';
const bin = process.platform === 'win32'
  ? path.join('node_modules', '.bin', 'genlayer.cmd')
  : path.join('node_modules', '.bin', 'genlayer');

function fail(message) {
  console.error(`KNOT toolchain guard: ${message}`);
  process.exit(1);
}

if (!existsSync(bin)) {
  fail('local GenLayer CLI is missing. Run npm install in this repository first.');
}

const versionOutput = execFileSync(bin, ['--version'], {
  encoding: 'utf8',
  shell: process.platform === 'win32',
}).trim();
if (!versionOutput.includes(EXPECTED_VERSION) || /0\.40|rc2/i.test(versionOutput)) {
  fail(`expected local GenLayer CLI ${EXPECTED_VERSION}; got: ${versionOutput}`);
}

const pkg = JSON.parse(readFileSync('package.json', 'utf8'));
if (pkg?.devDependencies?.genlayer !== EXPECTED_VERSION) {
  fail(`package.json must pin genlayer exactly to ${EXPECTED_VERSION}`);
}

const gltest = readFileSync('gltest.config.yaml', 'utf8');
if (!gltest.includes(EXPECTED_RPC) || !gltest.includes('studionet:')) {
  fail(`gltest.config.yaml must target stable Studionet ${EXPECTED_RPC}`);
}
if (/studio-dev|61997/i.test(gltest)) {
  fail('Studio-dev/61997 is forbidden in the active test configuration.');
}

console.log(`OK: local CLI ${EXPECTED_VERSION}`);
console.log(`OK: Studionet RPC ${EXPECTED_RPC}`);
console.log(`Expected deployment chain ID: ${EXPECTED_CHAIN}`);
