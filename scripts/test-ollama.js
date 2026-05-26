const http = require('http')
const https = require('https')
const { OLLAMA_API } = require('../lib/ollama')

async function test() {
  try {
    const url = new URL(OLLAMA_API)
    const isHttps = url.protocol === 'https:'
    const opts = { method: 'GET', hostname: url.hostname, port: url.port, path: url.pathname }
    const client = isHttps ? https : http
    const req = client.request(opts, (res) => {
      console.log('Ollama API status:', res.statusCode)
    })
    req.on('error', (e) => console.error('err', e))
    req.end()
  } catch (e) {
    console.error('Ollama API unreachable')
  }
}

test()
