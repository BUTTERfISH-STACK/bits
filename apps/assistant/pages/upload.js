import {useState} from 'react'

const ALLOWED_EXT = ['pdf','docx','doc','txt']
const MAX_BYTES = 5 * 1024 * 1024 // 5MB

export default function Upload() {
  const [file, setFile] = useState(null)
  const [jobTitle, setJobTitle] = useState('Product Manager')
  const [industry, setIndustry] = useState('Tech / SaaS')
  const [jobId, setJobId] = useState(null)
  const [error, setError] = useState(null)

  function onFileChange(e){
    setError(null)
    const f = e.target.files[0]
    if(!f) return setFile(null)
    const ext = f.name.split('.').pop().toLowerCase()
    if(!ALLOWED_EXT.includes(ext)){
      setError('Unsupported file type. Allowed: pdf, docx, doc, txt')
      return setFile(null)
    }
    if(f.size > MAX_BYTES){
      setError('File too large. Max 5 MB.')
      return setFile(null)
    }
    setFile(f)
  }

  async function upload() {
    setError(null)
    if(!file) return setError('No file selected')
    const form = new FormData()
    form.append('file', file)
    form.append('job_title', jobTitle)
    form.append('industry', industry)
    const res = await fetch(`/api/upload?tenant_id=11111111-1111-1111-1111-111111111111`, {method:'POST', body: form})
    if(!res.ok){
      const err = await res.json().catch(()=>({error:'upload failed'}))
      setError(err.error||'upload failed')
      return
    }
    const data = await res.json()
    setJobId(data.job_id)
  }

  return (
    <div style={{padding:20}}>
      <h1>Upload CV</h1>
      <input type="file" onChange={onFileChange} />
      {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
      <div style={{marginTop:8}}>
        <label>Job Title</label>
        <input value={jobTitle} onChange={e=>setJobTitle(e.target.value)} />
      </div>
      <div style={{marginTop:8}}>
        <label>Industry</label>
        <input value={industry} onChange={e=>setIndustry(e.target.value)} />
      </div>
      <button onClick={upload} disabled={!file} style={{marginTop:12}}>Upload</button>
      {jobId && <div style={{marginTop:12}}>Job submitted: {jobId}</div>}
    </div>
  )
}
