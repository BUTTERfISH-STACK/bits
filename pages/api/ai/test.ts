const handle = async (req, res) => {
  if (req.method === 'POST') {
    const { prompt } = req.body
    // Simple test endpoint for streaming simulation
    res.setHeader('Content-Type', 'text/event-stream')
    res.setHeader('Cache-Control', 'no-cache')
    res.write('data: {"status":"ok"}\n\n')
    res.end()
  } else {
    res.status(200).json({ status: 'ok' })
  }
}

module.exports = handle
