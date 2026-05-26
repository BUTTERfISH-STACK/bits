import React from 'react'

export default function AIStreamDemo() {
  const [out, setOut] = React.useState('')

  React.useEffect(() => {
    const es = new EventSource('/api/ai/generate')
    es.onmessage = (e) => setOut((s) => s + e.data)
    es.onerror = () => es.close()
    return () => es.close()
  }, [])

  return <pre className="p-4 bg-gray-900 rounded">{out}</pre>
}
