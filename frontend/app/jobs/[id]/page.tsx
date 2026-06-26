"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getJob, streamUrl, downloadUrl } from "@/lib/api";
import type { Job, Clip } from "@/lib/types";
import { STATUS_STEPS, RECIPES } from "@/lib/types";

const POLL_INTERVAL = 3000;

function ViralScoreBadge({ score }: { score: number }) {
  const pct = Math.min(100, Math.max(0, score));
  const color =
    pct >= 80 ? "text-green-400 bg-green-500/10 border-green-500/20" :
    pct >= 60 ? "text-yellow-400 bg-yellow-500/10 border-yellow-500/20" :
                "text-zinc-400 bg-zinc-500/10 border-zinc-500/20";
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold border ${color}`}>
      🔥 {pct}/100
    </span>
  );
}

function MomentBadge({ type }: { type: string }) {
  const map: Record<string, string> = {
    hook:           "bg-purple-500/20 text-purple-400",
    climax:         "bg-red-500/20 text-red-400",
    emotional_peak: "bg-pink-500/20 text-pink-400",
    funny:          "bg-yellow-500/20 text-yellow-400",
    question:       "bg-blue-500/20 text-blue-400",
    cta:            "bg-orange-500/20 text-orange-400",
    viral:          "bg-green-500/20 text-green-400",
  };
  const label = type.replace(/_/g, " ");
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium capitalize ${map[type] || "bg-zinc-500/20 text-zinc-400"}`}>
      {label}
    </span>
  );
}

function ClipCard({ clip, jobId }: { clip: Clip; jobId: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mins = Math.floor(clip.duration / 60);
  const secs = Math.round(clip.duration % 60);
  const duration = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;

  const title = clip.storylineTitle
    ? clip.storylineTitle.replace(/_/g, " ")
    : `Clip · ${clip.momentType}`;

  return (
    <div className="rounded-2xl bg-zinc-900 border border-zinc-800 overflow-hidden group hover:border-zinc-700 transition-all">
      {/* Video Preview */}
      <div className="relative aspect-[9/16] bg-zinc-950 overflow-hidden">
        <video
          ref={videoRef}
          src={streamUrl(jobId, clip.id)}
          className="w-full h-full object-cover"
          muted
          loop
          playsInline
          onMouseEnter={() => videoRef.current?.play()}
          onMouseLeave={() => { if (videoRef.current) { videoRef.current.pause(); videoRef.current.currentTime = 0; }}}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
          <MomentBadge type={clip.momentType} />
          <ViralScoreBadge score={clip.viralScore} />
        </div>
        <div className="absolute bottom-3 left-3 text-xs text-zinc-300 font-medium bg-black/50 px-2 py-0.5 rounded-full">
          {duration}
        </div>
        {/* Hover to play hint */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-5 h-5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-white capitalize text-sm truncate mb-1">{title}</h3>
        {clip.storylineSummary && (
          <p className="text-xs text-zinc-500 line-clamp-2 mb-3">{clip.storylineSummary}</p>
        )}
        <a
          href={downloadUrl(jobId, clip.id)}
          download
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          Download MP4
        </a>
      </div>
    </div>
  );
}

function StatusStepper({ status }: { status: string }) {
  const currentIdx = STATUS_STEPS.findIndex((s) => s.status === status);
  const isFailed = status === "FAILED";

  return (
    <div className="flex flex-col gap-0">
      {STATUS_STEPS.map((step, i) => {
        const done    = !isFailed && (i < currentIdx || status === "COMPLETE");
        const active  = !isFailed && i === currentIdx && status !== "COMPLETE";
        const pending = !done && !active;

        return (
          <div key={step.status} className="flex items-start gap-4">
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0
                ${done    ? "bg-green-500 text-white" :
                  active  ? "bg-purple-500 text-white ring-4 ring-purple-500/20" :
                  isFailed && i === currentIdx ? "bg-red-500 text-white" :
                  "bg-zinc-800 text-zinc-500"}`}
              >
                {done ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                ) : active ? (
                  <svg className="w-4 h-4 spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4" />
                  </svg>
                ) : (
                  <span>{i + 1}</span>
                )}
              </div>
              {i < STATUS_STEPS.length - 1 && (
                <div className={`w-0.5 h-8 mt-0.5 ${done ? "bg-green-500/40" : "bg-zinc-800"}`} />
              )}
            </div>
            <div className="pt-1.5 pb-8">
              <p className={`text-sm font-semibold ${done ? "text-green-400" : active ? "text-white" : "text-zinc-600"}`}>
                {step.label}
              </p>
              {(active || done) && (
                <p className="text-xs text-zinc-500 mt-0.5">{step.description}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function JobPage() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchJob = async () => {
    try {
      const data = await getJob(id);
      setJob(data);
      if (data.status === "COMPLETE" || data.status === "FAILED") {
        if (pollRef.current) clearInterval(pollRef.current);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load job");
    }
  };

  useEffect(() => {
    fetchJob();
    pollRef.current = setInterval(fetchJob, POLL_INTERVAL);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [id]);

  const recipe = RECIPES.find((r) => r.id === job?.recipe);

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-400 font-medium">{error}</p>
        <Link href="/" className="mt-4 inline-block text-sm text-zinc-400 hover:text-white">
          ← Back to upload
        </Link>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="h-8 w-48 shimmer rounded-lg mb-8" />
        <div className="h-64 shimmer rounded-2xl" />
      </div>
    );
  }

  const isComplete = job.status === "COMPLETE";
  const isFailed   = job.status === "FAILED";

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8 gap-4">
        <div>
          <Link href="/" className="text-sm text-zinc-500 hover:text-white transition-colors flex items-center gap-1 mb-3">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
            </svg>
            New video
          </Link>
          <h1 className="text-2xl font-bold text-white truncate">{job.videoName || "Unnamed video"}</h1>
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            {recipe && (
              <span className={`text-xs font-medium ${recipe.textColor}`}>
                {recipe.emoji} {recipe.label} style
              </span>
            )}
            <span className="text-zinc-600 text-xs">·</span>
            <span className="text-zinc-500 text-xs font-mono">{job.id.slice(0, 12)}…</span>
          </div>
        </div>
        {isComplete && job.clips.length > 0 && (
          <div className="shrink-0 text-right">
            <p className="text-2xl font-bold text-white">{job.clips.length}</p>
            <p className="text-xs text-zinc-500">clips ready</p>
          </div>
        )}
      </div>

      {isFailed ? (
        <div className="rounded-2xl bg-red-500/5 border border-red-500/20 p-8 text-center">
          <p className="text-4xl mb-3">❌</p>
          <p className="font-semibold text-red-400 text-lg mb-2">Processing failed</p>
          <p className="text-zinc-500 text-sm max-w-md mx-auto">{job.errorMessage || "An unexpected error occurred."}</p>
          <Link
            href="/"
            className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white text-sm font-medium transition-colors"
          >
            Try again
          </Link>
        </div>
      ) : !isComplete ? (
        <div className="grid sm:grid-cols-2 gap-8">
          <div className="bg-zinc-900 rounded-2xl border border-zinc-800 p-8">
            <h2 className="font-semibold text-white mb-6">Processing your video</h2>
            <StatusStepper status={job.status} />
          </div>
          <div className="flex flex-col items-center justify-center text-center p-8">
            <div className="w-20 h-20 rounded-2xl bg-purple-500/10 flex items-center justify-center mb-6">
              <svg className="w-10 h-10 text-purple-400 spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
              </svg>
            </div>
            <p className="text-zinc-400 text-sm leading-relaxed max-w-xs">
              Claude is analyzing your video for viral moments. This takes 2–10 minutes depending on length.
            </p>
            <p className="text-xs text-zinc-600 mt-4">Auto-refreshing every 3 seconds</p>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-semibold text-white">
              {job.clips.length} clip{job.clips.length !== 1 ? "s" : ""} ready
            </h2>
            <p className="text-xs text-zinc-500">Hover to preview · Click to download</p>
          </div>
          {job.clips.length === 0 ? (
            <div className="text-center py-16 text-zinc-500">
              <p className="text-4xl mb-4">🤔</p>
              <p>No viral moments found. Try a longer or more dynamic video.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {job.clips.map((clip) => (
                <ClipCard key={clip.id} clip={clip} jobId={job.id} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
