"use client";

import { useEffect, useRef, useState } from "react";

type Segment = {
  start: number;
  end: number;
  action: "cut" | "speedup";
  confidence: number;
  reasons: string[];
};

type Props = {
  videoSrc: string;
  durationSeconds?: number;
  segments: Segment[];
};

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function SyncedPreviewTimeline({
  videoSrc,
  durationSeconds,
  segments,
}: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [hoverTime, setHoverTime] = useState<number | null>(null);

  const total = durationSeconds || 1;

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    function handleTime() {
      setCurrentTime(video.currentTime);
    }

    video.addEventListener("timeupdate", handleTime);
    return () => video.removeEventListener("timeupdate", handleTime);
  }, []);

  function seekTo(seconds: number) {
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = Math.max(0, seconds);
    setCurrentTime(video.currentTime);
  }

  function handleTimelineClick(e: React.MouseEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    seekTo(ratio * total);
  }

  function handleTimelineMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    setHoverTime(Math.max(0, Math.min(total, ratio * total)));
  }

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Synced Preview Player</h3>

      <video
        ref={videoRef}
        controls
        className="mb-4 w-full rounded-2xl border"
        src={videoSrc}
      />

      <div
        className="relative mb-3 h-16 cursor-pointer rounded-xl bg-gray-100"
        onClick={handleTimelineClick}
        onMouseMove={handleTimelineMove}
        onMouseLeave={() => setHoverTime(null)}
      >
        {segments.map((seg, idx) => {
          const left = (seg.start / total) * 100;
          const width = ((seg.end - seg.start) / total) * 100;
          return (
            <div
              key={idx}
              title={`${seg.action}: ${formatTime(seg.start)} → ${formatTime(seg.end)}`}
              className={`absolute top-2 h-12 rounded-lg ${
                seg.action === "cut" ? "bg-red-400/80" : "bg-amber-400/80"
              }`}
              style={{
                left: `${left}%`,
                width: `${Math.max(width, 1)}%`,
              }}
            />
          );
        })}

        <div
          className="absolute top-0 h-16 w-1 bg-black"
          style={{ left: `${(currentTime / total) * 100}%` }}
        />

        {hoverTime !== null && (
          <>
            <div
              className="absolute top-0 h-16 w-px bg-blue-600"
              style={{ left: `${(hoverTime / total) * 100}%` }}
            />
            <div
              className="absolute -top-8 rounded bg-black px-2 py-1 text-xs text-white"
              style={{ left: `calc(${(hoverTime / total) * 100}% - 18px)` }}
            >
              {formatTime(hoverTime)}
            </div>
          </>
        )}
      </div>

      <div className="flex justify-between text-xs text-gray-500">
        <span>{formatTime(currentTime)}</span>
        <span>{formatTime(total)}</span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <button
          onClick={() => seekTo(Math.max(0, currentTime - 5))}
          className="rounded-xl border px-4 py-2"
        >
          -5s
        </button>
        <button
          onClick={() => seekTo(Math.min(total, currentTime + 5))}
          className="rounded-xl border px-4 py-2"
        >
          +5s
        </button>
      </div>
    </div>
  );
}
