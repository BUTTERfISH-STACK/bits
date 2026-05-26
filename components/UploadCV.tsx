import React from 'react'

export default function UploadCV() {
  const fileRef = React.useRef<HTMLInputElement | null>(null)
  return (
    <div>
      <input ref={fileRef} type="file" accept=".pdf,.doc,.docx,.txt" />
    </div>
  )
}
