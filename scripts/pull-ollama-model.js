const { execSync, spawn } = require('child_process')

function listModels() {
  try {
    const out = execSync('ollama list --json', { encoding: 'utf8' })
    return JSON.parse(out)
  } catch (e) {
    return null
  }
}

function pullModel(model) {
  console.log('Pulling model', model)
  execSync(`ollama pull ${model}`, { stdio: 'inherit' })
}

function startDaemon() {
  console.log('Attempting to start Ollama daemon...')
  const p = spawn('ollama', ['daemon'], { detached: true, stdio: 'ignore' })
  p.unref()
}

async function waitForDaemon(timeout = 60000) {
  const start = Date.now()
  while (Date.now() - start < timeout) {
    if (listModels() !== null) return true
    await new Promise((r) => setTimeout(r, 2000))
  }
  return false
}

try {
  const required = ['qwen2.5:7b']
  let models = listModels()
  if (!models) {
    startDaemon()
    const ok = await waitForDaemon()
    if (!ok) throw new Error('Ollama daemon did not start')
    models = listModels()
  }
  for (const m of required) {
    const exists = models.some((x) => x.model === m)
    if (!exists) pullModel(m)
  }
  console.log('Ollama ready')
} catch (err) {
  console.error('Ollama setup failed', err)
  process.exit(1)
}
