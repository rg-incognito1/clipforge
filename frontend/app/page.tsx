"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { createJob } from "@/lib/api";
import { RECIPES } from "@/lib/types";

export default function Home() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [recipe, setRecipe] = useState("mrbeast");
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const onFileSelect = (f: File) => {
    const allowed = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/webm", "video/mpeg"];
    if (!allowed.includes(f.type) && !f.name.match(/\.(mp4|mov|avi|webm|mkv|mpeg)$/i)) {
      setError("Please upload a video file (MP4, MOV, AVI, WebM)");
      return;
    }
    setError("");
    setFile(f);
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFileSelect(f);
  }, []);

  const handleSubmit = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const { jobId } = await createJob(file, recipe, "9:16");
      router.push(`/jobs/${jobId}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero */}
      <div className="text-center mb-12 pt-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-medium mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
          Powered by Claude AI + Whisper
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
          Turn any video into{" "}
          <span className="bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
            viral shorts
          </span>
        </h1>
        <p className="text-zinc-400 text-lg max-w-xl mx-auto">
          AI finds the best moments, auto-crops to vertical, burns styled captions, and delivers ready-to-post clips.
        </p>
      </div>

      {/* Upload Zone */}
      <div
        className={`relative rounded-2xl border-2 border-dashed transition-all duration-200 cursor-pointer mb-8
          ${dragging
            ? "border-purple-500 bg-purple-500/10"
            : file
            ? "border-purple-500/50 bg-purple-500/5"
            : "border-zinc-700 bg-zinc-900/50 hover:border-zinc-600 hover:bg-zinc-900"
          }`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && onFileSelect(e.target.files[0])}
        />
        <div className="py-14 px-8 text-center">
          {file ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-14 h-14 rounded-xl bg-purple-500/20 flex items-center justify-center">
                <svg className="w-7 h-7 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                </svg>
              </div>
              <p className="font-semibold text-white text-lg">{file.name}</p>
              <p className="text-zinc-500 text-sm">{(file.size / 1024 / 1024).toFixed(1)} MB · Click to change</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <div className="w-14 h-14 rounded-xl bg-zinc-800 flex items-center justify-center">
                <svg className="w-7 h-7 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-white text-lg">Drop your video here</p>
                <p className="text-zinc-500 text-sm mt-1">MP4, MOV, AVI, WebM · Up to 4 hours</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recipe Selector */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">Caption Style</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {RECIPES.map((r) => (
            <button
              key={r.id}
              onClick={() => setRecipe(r.id)}
              className={`relative p-4 rounded-xl border bg-gradient-to-b text-left transition-all duration-150
                ${recipe === r.id
                  ? `${r.color} ring-1 ring-purple-500/50`
                  : "border-zinc-800 bg-zinc-900/50 hover:border-zinc-700"
                }`}
            >
              {recipe === r.id && (
                <div className="absolute top-3 right-3 w-2 h-2 rounded-full bg-purple-400" />
              )}
              <div className="text-2xl mb-2">{r.emoji}</div>
              <p className={`font-semibold text-sm ${recipe === r.id ? r.textColor : "text-white"}`}>
                {r.label}
              </p>
              <p className="text-zinc-500 text-xs mt-0.5 leading-relaxed">{r.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* CTA */}
      <button
        onClick={handleSubmit}
        disabled={!file || uploading}
        className={`w-full py-4 rounded-xl font-semibold text-base transition-all duration-150
          ${!file || uploading
            ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
            : "bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white shadow-lg shadow-purple-500/20 hover:shadow-purple-500/30"
          }`}
      >
        {uploading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="w-4 h-4 spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
            Uploading & Queuing...
          </span>
        ) : (
          "Generate Shorts →"
        )}
      </button>

      {/* Features strip */}
      <div className="mt-16 pt-12 border-t border-zinc-800/60">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
          {[
            { icon: "🧠", label: "AI Scene Detection", desc: "Finds hooks, climaxes, viral moments" },
            { icon: "📐", label: "Smart Crop", desc: "Face-tracked 9:16 auto-reframing" },
            { icon: "✍️", label: "Styled Captions", desc: "6 styles with word-level highlights" },
            { icon: "⚡", label: "Batch Ready", desc: "Multiple clips per video, parallel" },
          ].map((f) => (
            <div key={f.label} className="flex flex-col items-center gap-2">
              <span className="text-2xl">{f.icon}</span>
              <p className="text-sm font-semibold text-white">{f.label}</p>
              <p className="text-xs text-zinc-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
