
import React, { useState } from "react";

export default function UploadImage() {
  const [result, setResult] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);

  async function handleUpload(e) {
    const file = e.target.files[0];
    setImageUrl(URL.createObjectURL(file));
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("https://lendr-backend.onrender.com/analyze-image", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResult(data);
  }

  return (
    <div style={{ padding: 20 }}>
      <input type="file" onChange={handleUpload} />
      {imageUrl && <img src={imageUrl} alt="Preview" style={{ marginTop: 10, maxWidth: "100%" }} />}
      {result && (
        <pre style={{ marginTop: 20, textAlign: "left" }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
