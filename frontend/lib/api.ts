import type { Job } from "./types";

const BASE = "/api/jobs";

export async function createJob(
  file: File,
  recipe: string,
  formats: string
): Promise<{ jobId: string; videoName: string }> {
  const form = new FormData();
  form.append("file", file);
  form.append("recipe", recipe);
  form.append("formats", formats);

  const res = await fetch(BASE, { method: "POST", body: form });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed (${res.status}): ${text}`);
  }
  return res.json();
}

export async function getJob(id: string): Promise<Job> {
  const res = await fetch(`${BASE}/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Job not found: ${id}`);
  return res.json();
}

export async function listJobs(): Promise<Job[]> {
  const res = await fetch(BASE, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to list jobs");
  return res.json();
}

export function streamUrl(jobId: string, clipId: string) {
  return `${BASE}/${jobId}/clips/${clipId}/stream`;
}

export function downloadUrl(jobId: string, clipId: string) {
  return `${BASE}/${jobId}/clips/${clipId}/download`;
}
