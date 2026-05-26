// apps/assistant/pages/index.js
import {useState} from 'react'

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([])

  async function send() {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: 's1', user_id: '22222222-2222-2222-2222-222222222222', tenant_id: '11111111-1111-1111-1111-111111111111', prompt })
    })
    const data = await res.json()
    setMessages([...messages, {role: 'assistant', text: data.text || JSON.stringify(data)}])
  }

  return (
    <div style={{padding:20}}>
      <h1>Assistant Chat</h1>
      <div style={{marginBottom:10}}>
        <textarea value={prompt} onChange={e=>setPrompt(e.target.value)} rows={4} cols={80}></textarea>
      </div>
      <button onClick={send}>Send</button>
      <div style={{marginTop:20}}>
        {messages.map((m,i)=>(<div key={i}><b>{m.role}:</b> {m.text}</div>))}
      </div>
    </div>
  )
}
