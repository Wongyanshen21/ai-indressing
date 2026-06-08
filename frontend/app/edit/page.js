"use client";

import { useState, useEffect, useRef } from "react";

export default function EditPage() {
  const [presets, setPresets] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");
  const [file, setFile] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetch("/api/presets")
      .then((r) => r.json())
      .then((data) => setPresets(data.presets || []))
      .catch(() => {});
  }, []);

  const handlePresetClick = (prompt) => {
    setSelectedPrompt(prompt);
    setCustomPrompt("");
  };

  const handleSubmit = async () => {
    const prompt = customPrompt || selectedPrompt;
    if (!file || !prompt) return;

    setLoading(true);
    setStatus("Uploading photo...");
    setResultUrl(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      setStatus("Analyzing clothing...");
      const segRes = await fetch("/api/segment", { method: "POST", body: formData });
      if (!segRes.ok) throw new Error("Segmentation failed");
      const maskBlob = await segRes.blob();

      const inpaintForm = new FormData();
      inpaintForm.append("file", file);
      inpaintForm.append("mask", maskBlob, "mask.png");
      inpaintForm.append("prompt", prompt);

      setStatus("Generating new outfit...");
      const inpaintRes = await fetch("/api/inpaint", { method: "POST", body: inpaintForm });
      if (!inpaintRes.ok) throw new Error("Inpainting failed");

      const resultBlob = await inpaintRes.blob();
      setResultUrl(URL.createObjectURL(resultBlob));
      setStatus("");
    } catch (e) {
      setStatus("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
      <h1>Edit Photo</h1>
      <p style={{ marginBottom: 24, color: "#666" }}>
        Upload a photo, then choose or write what you want the AI to change your clothes to.
      </p>

      <div style={{ marginBottom: 24 }}>
        <label
          style={{
            display: "block",
            padding: 32,
            border: "2px dashed #ccc",
            borderRadius: 8,
            textAlign: "center",
            cursor: "pointer",
            background: "#fafafa",
          }}
        >
          {file ? (
            <span>Selected: {file.name}</span>
          ) : (
            <span>Click to upload a photo</span>
          )}
          <input
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={(e) => setFile(e.target.files[0])}
          />
        </label>
      </div>

      <div style={{ marginBottom: 16 }}>
        <h3 style={{ marginBottom: 12 }}>Choose a style</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {presets.map((p, i) => (
            <button
              key={i}
              onClick={() => handlePresetClick(p.prompt)}
              style={{
                padding: "12px 16px",
                border: selectedPrompt === p.prompt ? "2px solid #0070f3" : "1px solid #ddd",
                borderRadius: 6,
                background: selectedPrompt === p.prompt ? "#e8f4fd" : "#fff",
                cursor: "pointer",
                fontSize: 14,
                textAlign: "center",
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3 style={{ marginBottom: 8 }}>Or write your own</h3>
        <input
          type="text"
          placeholder="e.g. a red plaid shirt with dark jeans"
          value={customPrompt}
          onChange={(e) => { setCustomPrompt(e.target.value); setSelectedPrompt(""); }}
          style={{
            width: "100%",
            padding: "10px 12px",
            border: "1px solid #ccc",
            borderRadius: 6,
            fontSize: 14,
          }}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !file || (!selectedPrompt && !customPrompt)}
        style={{
          width: "100%",
          padding: "14px",
          fontSize: 16,
          fontWeight: 600,
          border: "none",
          borderRadius: 6,
          background: loading || !file || (!selectedPrompt && !customPrompt) ? "#ccc" : "#28a745",
          color: "#fff",
          cursor: loading || !file || (!selectedPrompt && !customPrompt) ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Processing..." : "Indress My Photo"}
      </button>

      {status && <p style={{ marginTop: 16, textAlign: "center", color: "#666" }}>{status}</p>}

      {resultUrl && (
        <div style={{ marginTop: 24, textAlign: "center" }}>
          <h3>Result</h3>
          <img src={resultUrl} alt="Result" style={{ maxWidth: "100%", borderRadius: 8, marginTop: 8 }} />
        </div>
      )}
    </div>
  );
}
