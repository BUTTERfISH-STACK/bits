// apps/assistant/pages/upload.js
import {useState} from 'react'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [jobTitle, setJobTitle] = useState('Product Manager')
  const [industry, setIndustry] = useState('Tech / SaaS')
  const [jobId, setJobId] = useState(null)

  async function upload() {
    const form = new FormData()
    form.append('file', file)
    form.append('job_title', jobTitle)
    form.append('industry', industry)
    const res = await fetch(`/api/upload?tenant_id=11111111-1111-1111-1111-111111111111`, {method:'POST', body: form})
    const data = await res.json()
    setJobId(data.job_id)
  }

  return (
    <div style={{padding:20}}>
      <h1>Upload CV</h1>
      <input type="file" onChange={e=>setFile(e.target.files[0])} />
      <div>
        <label>Job Title</label>
        <input value={jobTitle} onChange={e=>setJobTitle(e.target.value)} />
      </div>
      <div>
        <label>Industry</label>
        <input value={industry} onChange={e=>setIndustry(e.target.value)} />
      </div>
      <button onClick={upload} disabled={!file}>Upload</button>
      {jobId && <div>Job submitted: {jobId}</div>}
    </div>
  )
}
