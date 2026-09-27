import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';

const EXPECTED_VERSION = '0.39.1';
const EXPECTED_RPC = 'https://studio.genlayer.com/api';
const EXPECTED_CHAIN = '61999';
const bin = process.platform === 'win32'
  ? path.join('node_modules', '.bin', 'genlayer.cmd')
  : path.join('node_modules', '.bin', 'genlayer');

function fail(message) {
  console.error(`KNOT deploy guard: ${message}`);
  process.exit(1);
}

if (!existsSync(bin)) fail('run npm install first; local genlayer CLI is missing');
const version = execFileSync(bin, ['--version'], { encoding: 'utf8' }).trim();
if (!version.includes(EXPECTED_VERSION) || /0\.40|rc2/i.test(version)) {
  fail(`refusing deployment with ${version}; KNOT requires local CLI ${EXPECTED_VERSION}`);
}

execFileSync(bin, ['network', 'set', 'studionet'], { stdio: 'inherit' });
const info = execFileSync(bin, ['network', 'info'], { encoding: 'utf8' });
console.log(info);
if (!info.includes(EXPECTED_CHAIN) || !info.includes('studio.genlayer.com')) {
  fail(`network info did not prove stable Studionet chain ${EXPECTED_CHAIN}`);
}

console.log(`Deploying KNOT to stable Studionet ${EXPECTED_CHAIN} via ${EXPECTED_RPC}`);
execFileSync(
  bin,
  ['deploy', '--contract', 'contracts/knot.py', '--rpc', EXPECTED_RPC],
  { stdio: 'inherit' },
);
