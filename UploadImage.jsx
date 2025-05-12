import React, { useState } from "react";

const BACKENDS = [
  "https://p-659806.onrender.com/analyze-image",
  "https://p-659806.fly.dev/analyze-image",
  "https://lendr-backend.onrender.com/analyze-image",
];

export default function UploadImage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [responseData, setResponseData] = useState(null);

  const getPreferredBackend = () => {
    const cached = localStorage.getItem("workingBackend");
    return cached || BACKENDS[0];
  };

  const testAndFallback = async (formData) => {
    for (const url of BACKENDS) {
      try {
        const response = await fetch(url, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          localStorage.setItem("workingBackend", url); // cache success
          return await response.json();
        }

        console.warn(`⚠️ Backend failed: ${url}`);
      } catch (e) {
        console.error(`❌ Error with backend ${url}:`, e);
      }
    }
    throw new Error("All backend services are unavailable.");
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) {
      console.error("No file selected");
      return;
    }

    setSelectedImage(URL.createObjectURL(file));
    handleUpload(file);
  };

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const result = await testAndFallback(formData);
      const data = result.raw ? JSON.parse(result.raw) : result;

      console.log("✅ Parsed result:", data);
      setResponseData(data);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("All image processing servers are currently down. Please try again later.");
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <h2 className="text-xl font-bold">Upload an image to analyze</h2>
      <input type="file" accept="image/*" onChange={handleImageChange} />
      {selectedImage && <img src={selectedImage} alt="Preview" className="w-64 mt-4" />}
      {responseData && (
        <div className="mt-4 text-left">
          <h3 className="font-semibold">Results:</h3>
          <pre className="text-sm">{JSON.stringify(responseData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
