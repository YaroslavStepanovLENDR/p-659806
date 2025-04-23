// test
import React, { useState } from "react";

export default function UploadImage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [responseData, setResponseData] = useState(null);

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
    formData.append("file", file); // 👈 must be named "file"

    console.log("Uploading file:", file);

    try {
      const response = await fetch("https://lendr-backend.onrender.com/analyze-image", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      const data = result.raw ? JSON.parse(result.raw) : result;

      console.log("Parsed result:", data);
      setResponseData(data);
    } catch (error) {
      console.error("Upload failed:", error);
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
