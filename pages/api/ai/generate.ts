const fetch = require('../../node-fetch-shim')
const { OLLAMA_API, REQUIRED_MODELS } = require('../../../lib/ollama')

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end()
  const { prompt, model } = req.body
  const usedModel = model || 'qwen2.5:7b'

  const payload = {
    model: usedModel,
    prompt: [{ role: 'user', content: prompt }],
    stream: true,
    max_tokens: 1000,
  }

  try {
    const response = await fetch(OLLAMA_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      for (const fb of REQUIRED_MODELS) {
        const r2 = await fetch(OLLAMA_API, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...payload, model: fb }),
        })
        if (r2.ok) return r2.body.pipe(res)
      }
      return res.status(502).json({ error: 'Ollama generate failed' })
    }

    // stream response back
    res.setHeader('Content-Type', 'text/event-stream')
    res.setHeader('Cache-Control', 'no-cache')
    res.setHeader('Connection', 'keep-alive')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value)
      res.write(`data: ${chunk}\n\n`)
    }
    res.end()
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}
