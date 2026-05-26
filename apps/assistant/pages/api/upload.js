# Frontend API proxy for upload

// apps/assistant/pages/api/upload.js

import formidable from 'formidable'
import fs from 'fs'

export const config = {
  api: {
    bodyParser: false
  }
}

export default async function handler(req, res) {
  const form = new formidable.IncomingForm()
  form.parse(req, async (err, fields, files) => {
    if (err) return res.status(500).json({error: 'parse error'})
    const file = files.file
    const data = new FormData()
    data.append('file', fs.createReadStream(file.filepath), file.originalFilename)
    data.append('job_title', fields.job_title || '')
    data.append('industry', fields.industry || '')

    const resp = await fetch(`http://localhost:8090/v1/tenants/${req.query.tenant_id}/cv/upload`, {method:'POST', body: data})
    const json = await resp.json()
    res.status(200).json(json)
  })
}
