#!/usr/bin/env node
// Run a command with Algolia credentials read from a Vercel-pulled env file.
//
//   node scripts/with-algolia-env.mjs <env-file> <key-var> -- <command> [args...]
//
// <key-var> is the variable holding the key for this command, e.g.
// ALGOLIA_WRITE_API_KEY for an import, ALGOLIA_SEARCH_API_KEY for a validation query.
//
// The file is PARSED (node:util parseEnv), never sourced: `$(...)`, backticks and `&&`
// in a value stay literal text. Only ALGOLIA_APPLICATION_ID and ALGOLIA_API_KEY are
// overridden, and the parsed file wins over whatever is already in the ambient
// environment, so a stale export cannot silently point at a different application.
// Values are never printed.
//
// Requires Node >= 20.12 (parseEnv).

import { readFileSync } from 'node:fs';
import { parseEnv } from 'node:util';
import { spawnSync } from 'node:child_process';

const [envFile, keyVar, separator, ...command] = process.argv.slice(2);

if (!envFile || !keyVar || separator !== '--' || command.length === 0) {
  console.error(
    'usage: with-algolia-env.mjs <env-file> <ALGOLIA_SEARCH_API_KEY|ALGOLIA_WRITE_API_KEY> -- <command> [args...]',
  );
  process.exit(2);
}

let parsed;
try {
  parsed = parseEnv(readFileSync(envFile, 'utf8'));
} catch (error) {
  console.error(`cannot read ${envFile}: ${error.code ?? error.message}`);
  process.exit(2);
}

const appId = parsed.ALGOLIA_APP_ID;
const apiKey = parsed[keyVar];
const missing = [!appId && 'ALGOLIA_APP_ID', !apiKey && keyVar].filter(Boolean);

if (missing.length > 0) {
  console.error(
    `missing in ${envFile}: ${missing.join(', ')} — check "vercel env ls" and that the resource is connected to this project`,
  );
  process.exit(2);
}

const { status, signal, error } = spawnSync(command[0], command.slice(1), {
  stdio: 'inherit',
  env: {
    ...process.env,
    ALGOLIA_APPLICATION_ID: appId,
    ALGOLIA_API_KEY: apiKey,
  },
});

if (error) {
  console.error(`cannot run ${command[0]}: ${error.code ?? error.message}`);
  process.exit(127);
}

process.exit(status ?? (signal ? 128 : 1));
