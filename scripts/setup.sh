#!/usr/bin/env node
const { execSync } = require('child_process')

function run(cmd) {
  console.log('> ' + cmd)
  execSync(cmd, { stdio: 'inherit' })
}

try {
  run('npm run pull-ollama-model')
  console.log('setup complete')
} catch (e) {
  console.error('setup failed', e)
  process.exit(1)
}
