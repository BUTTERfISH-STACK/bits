"use client"

import React from 'react'

export default function AIStreamComponent() {
  const [log, setLog] = React.useState('')

  React.useEffect(() => {
    let cancelled = false
    async function start() {
      const res = await fetch('/api/ai/generate', { method: 'POST', body: JSON.stringify({ prompt: 'test' }), headers: { 'Content-Type': 'application/json' } })
      if (!res.body) return
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      while (!cancelled) {
        const { done, value } = await reader.read()
        if (done) break
        setLog((s) => s + decoder.decode(value))
      }
    }
    start()
    return () => { cancelled = true }
  }, [])

  return <pre className="p-4 bg-black text-white">{log}</pre>
}
