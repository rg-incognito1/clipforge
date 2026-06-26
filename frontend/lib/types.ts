export type JobStatus =
  | "QUEUED"
  | "TRANSCRIBING"
  | "ANALYZING"
  | "PROCESSING"
  | "COMPLETE"
  | "FAILED";

export interface Clip {
  id: string;
  startSeconds: number;
  endSeconds: number;
  duration: number;
  momentType: string;
  viralScore: number;
  storylineTitle: string;
  storylineSummary: string;
}

export interface Job {
  id: string;
  status: JobStatus;
  recipe: string;
  formats: string;
  videoName: string;
  errorMessage: string;
  createdAt: string;
  clips: Clip[];
}

export const RECIPES = [
  {
    id: "mrbeast",
    label: "MrBeast",
    description: "Bold yellow highlights, Anton font, high-energy bounce",
    emoji: "⚡",
    color: "from-yellow-500/20 to-yellow-600/10 border-yellow-500/30",
    textColor: "text-yellow-400",
  },
  {
    id: "netflix",
    label: "Netflix",
    description: "Clean white captions with cinematic orange highlights",
    emoji: "🎬",
    color: "from-red-500/20 to-red-600/10 border-red-500/30",
    textColor: "text-red-400",
  },
  {
    id: "minimal",
    label: "Minimal",
    description: "Understated white text, subtle shadow, no distractions",
    emoji: "✦",
    color: "from-zinc-500/20 to-zinc-600/10 border-zinc-500/30",
    textColor: "text-zinc-300",
  },
  {
    id: "tiktok",
    label: "TikTok",
    description: "Punchy white fills, thick outline, scroll-stopping style",
    emoji: "🎵",
    color: "from-pink-500/20 to-pink-600/10 border-pink-500/30",
    textColor: "text-pink-400",
  },
  {
    id: "hormozi",
    label: "Hormozi",
    description: "Heavy black font, red highlights, no-BS direct style",
    emoji: "🔴",
    color: "from-orange-500/20 to-orange-600/10 border-orange-500/30",
    textColor: "text-orange-400",
  },
  {
    id: "podcast",
    label: "Podcast",
    description: "Georgia serif, green speaker highlights, editorial feel",
    emoji: "🎙",
    color: "from-green-500/20 to-green-600/10 border-green-500/30",
    textColor: "text-green-400",
  },
] as const;

export const STATUS_STEPS: { status: JobStatus; label: string; description: string }[] = [
  { status: "QUEUED",       label: "Queued",       description: "Job is waiting in the queue" },
  { status: "TRANSCRIBING", label: "Transcribing", description: "Whisper is converting audio to text" },
  { status: "ANALYZING",    label: "Analyzing",    description: "Claude is finding the best moments" },
  { status: "PROCESSING",   label: "Processing",   description: "Reframing, captioning & rendering clips" },
  { status: "COMPLETE",     label: "Complete",     description: "Your shorts are ready!" },
];
