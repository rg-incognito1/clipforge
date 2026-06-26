"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listJobs } from "@/lib/api";
import type { Job } from "@/lib/types";

function statusBadge(status: string) {
  const map: Record<string, string> = {
    QUEUED:       "bg-zinc-700 text-zinc-300",
    TRANSCRIBING: "bg-blue-500/20 text-blue-400",
    ANALYZING:    "bg-purple-500/20 text-purple-400",
    PROCESSING:   "bg-yellow-500/20 text-yellow-400",
    COMPLETE:     "bg-green-500/20 text-green-400",
    FAILED:       "bg-red-500/20 text-red-400",
  };
  return map[status] || "bg-zinc-700 text-zinc-300";
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listJobs()
      .then(setJobs)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">My Clips</h1>
        <Link
          href="/"
          className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium transition-colors"
        >
          + New Video
        </Link>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-xl shimmer" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 text-zinc-500">
          <p className="text-5xl mb-4">🎬</p>
          <p className="font-medium text-zinc-300 mb-1">No clips yet</p>
          <p className="text-sm">Upload a video to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <Link
              key={job.id}
              href={`/jobs/${job.id}`}
              className="block p-5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <p className="font-medium text-white truncate">
                    {job.videoName || "Unnamed video"}
                  </p>
                  <p className="text-xs text-zinc-500 mt-0.5">
                    {job.createdAt ? new Date(job.createdAt).toLocaleString() : ""}
                    {job.clips.length > 0 && ` · ${job.clips.length} clip${job.clips.length > 1 ? "s" : ""}`}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusBadge(job.status)}`}>
                    {job.status}
                  </span>
                  <svg className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
