// apps/assistant/pages/api/chat.js
export default async function handler(req, res) {
  const body = req.body
  const resp = await fetch('http://localhost:8081/v1/assistant/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  const data = await resp.json()
  res.status(200).json(data)
}
