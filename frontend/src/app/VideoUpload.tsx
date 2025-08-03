"use client";
import React, { useEffect, useState, useRef } from "react";
import Hls from "hls.js";

export default function VideoUpload() {
  const [uploadedVideoName, setUploadedVideoName] = useState<string | null>(null);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<null | { 
    detected_species: string[]; 
    confidence_scores: number[] 
  }>(null);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file && !file.type.startsWith('video/')) {
      setError('Please select a video file');
      return;
    }

    setVideoSrc(null);
    setVideoFile(file);
    setResult(null);
    setError(null);
    setUploadedVideoName(null);
    setRetryCount(0);
  };

  const handleUpload = async () => {
    if (!videoFile) return;

    setUploading(true);
    setProcessing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("video", videoFile);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

      const uploadResponse = await fetch(`${backendUrl}/predict/video`, {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json().catch(() => ({}));
        throw new Error(errorData.message || "Failed to upload or process video");
      }

      const resultData = await uploadResponse.json();

      // Get HLS path from backend
      const hlsUrl = `${backendUrl}${resultData.hls_url}`;
      setVideoSrc(hlsUrl);
      setUploadedVideoName(videoFile.name);

      // Optional: resultData may contain species info
      if (resultData.detected_species) {
        setResult({
          detected_species: resultData.detected_species,
          confidence_scores: resultData.confidence_scores,
        });
      }

      setRetryCount(0);

    } catch (err) {
      console.error("Upload error:", err);
      setError(err instanceof Error ? err.message : "An unknown error occurred during processing");
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  };

  // HLS attach to <video> element
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !videoSrc || !videoSrc.endsWith(".m3u8")) return;

    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(video);

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error("HLS error", data);
        setError("Error playing video. Try re-uploading.");
      });

      return () => hls.destroy();
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = videoSrc;
    } else {
      setError("HLS not supported in this browser.");
    }
  }, [videoSrc]);

  return (
    <div className="w-full max-w-xl mx-auto p-6 bg-white rounded-lg shadow-lg flex flex-col gap-6">
      <h2 className="text-2xl font-bold mb-2 text-center">Marine Life Detection</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Select Video File</label>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={!videoFile || uploading}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 
            disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? "Uploading..." : processing ? "Processing..." : "Upload & Detect"}
        </button>

        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-md">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 p-4 bg-gray-50 rounded-md">
            <h3 className="text-lg font-semibold mb-2">Detection Results:</h3>
            <div className="bg-white p-3 rounded border border-gray-200">
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}

        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2">Processed Video:</h3>
          <div className="bg-gray-50 p-4 rounded-md">
            {!videoSrc ? (
              <div className="text-center py-8 text-gray-500">
                {processing ? "Video is being processed..." : "No video processed yet"}
              </div>
            ) : (
              <div className="space-y-3">
                <video
                  ref={videoRef}
                  controls
                  autoPlay
                  muted
                  playsInline
                  className="rounded-md border border-gray-200 bg-black w-full"
                />
                {uploadedVideoName && (
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500 truncate">{uploadedVideoName}</span>
                    <a
                      href={videoSrc}
                      download={`processed_${uploadedVideoName}.m3u8`}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      Download Playlist
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
