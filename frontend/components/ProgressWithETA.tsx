"use client";

import { useEffect, useMemo, useState } from "react";

type Props = {
  progress: number;
  stage?: string | null;
  activityText?: string | null;
  isDone?: boolean;
};

function formatTime(sec: number) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s}s`;
}

export default function ProgressWithETA({
  progress,
  stage,
  activityText,
  isDone = false,
}: Props) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (isDone) return;

    const startedAt = Date.now();
    const interval = setInterval(() => {
      const diff = Math.floor((Date.now() - startedAt) / 1000);
      setElapsed(diff);
    }, 1000);

    return () => clearInterval(interval);
  }, [isDone]);

  const averageSpeed = useMemo(() => {
    if (elapsed <= 0 || progress <= 0) return 0;
    return progress / elapsed;
  }, [elapsed, progress]);

  const etaSeconds = useMemo(() => {
    if (progress >= 100) return 0;
    if (averageSpeed <= 0) return null;
    return Math.round((100 - progress) / averageSpeed);
  }, [progress, averageSpeed]);

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h3 className="mb-3 text-lg font-semibold">Analysis Progress</h3>

      <div className="mb-3 h-3 w-full rounded bg-gray-200">
        <div className="h-3 rounded bg-black" style={{ width: `${progress}%` }} />
      </div>

      <div className="text-sm text-gray-700">
        {progress}% • Elapsed: {formatTime(elapsed)}
        {etaSeconds !== null ? ` • ETA: ${formatTime(etaSeconds)}` : " • ETA: Calculating..."}
      </div>

      {averageSpeed > 0 && (
        <div className="mt-1 text-sm text-gray-500">
          Avg speed: {averageSpeed.toFixed(2)}% / sec
        </div>
      )}

      {stage && (
        <div className="mt-2 text-sm text-gray-500">
          Stage: {stage}
        </div>
      )}

      {activityText && (
        <div className="mt-1 text-sm text-gray-600">
          Working: {activityText}
        </div>
      )}
    </div>
  );
}
