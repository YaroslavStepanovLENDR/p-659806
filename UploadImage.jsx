import React, { useState } from 'react'

export default function UploadImage() {
  const [result, setResult] = useState(null)

  async function handleUpload(e) {
    const file = e.target.files[0]
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch('https://lendr-backend.onrender.com/analyze-image', {
      method: 'POST',
      body: formData
    })

    const data = await res.json()
    setResult(data)
  }

return (
  <div style={{ padding: 20, backgroundColor: "lightblue", minHeight: "100vh" }}>
    <h1>🚀 THIS IS THE NEW VERSION</h1>
    <h2>Upload Image to LENDR</h2>
    <input type="file" onChange={handleUpload} />
    {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
  </div>
)

}
