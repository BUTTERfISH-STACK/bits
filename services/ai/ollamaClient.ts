const fetch = require('../node-fetch-shim')
const { OLLAMA_API, REQUIRED_MODELS } = require('../lib/ollama')

async function generate(prompt, model) {
  const used = model || 'qwen2.5:7b'
  try {
    const res = await fetch(OLLAMA_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: used, prompt: [{ role: 'user', content: prompt }], stream: false, max_tokens: 1000 }),
      timeout: 300000,
    })
    if (res.ok) return await res.json()
    // try fallbacks
    for (const fb of REQUIRED_MODELS) {
      const r2 = await fetch(OLLAMA_API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model: fb, prompt: [{ role: 'user', content: prompt }], stream: false, max_tokens: 1000 }) })
      if (r2.ok) return await r2.json()
    }
    throw new Error('All models failed')
  } catch (e) {
    throw e
  }
}

module.exports = { generate }
