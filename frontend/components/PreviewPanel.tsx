"use client";

import SyncedPreviewTimeline from "@/components/SyncedPreviewTimeline";
import { previewDownloadUrl } from "@/lib/api";

type Segment = {
  start: number;
  end: number;
  action: "cut" | "speedup";
  confidence: number;
  reasons: string[];
};

type Props = {
  jobId: string;
  jobStatus: string;
  previewStatus?: string;
  previewError?: string | null;
  durationSeconds?: number;
  segments: Segment[];
};

export default function PreviewPanel({
  jobId,
  jobStatus,
  previewStatus,
  previewError,
  durationSeconds,
  segments,
}: Props) {
  const videoUrl = previewDownloadUrl(jobId);
  const isReady = previewStatus === "ready";

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold">Edited Video</h3>

        {jobStatus === "failed" || previewStatus === "failed" ? (
          <p className="rounded-xl bg-red-50 p-3 text-sm text-red-700">
            {previewError || "Edited video could not be created."}
          </p>
        ) : !isReady ? (
          <div className="space-y-2 text-sm text-gray-600">
            <p>The edited video is being prepared automatically.</p>
            <p>
              Status: <span className="font-medium">{previewStatus || "waiting"}</span>
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">Your watchable edited result is ready below.</p>
            <video
              key={videoUrl}
              src={videoUrl}
              controls
              playsInline
              className="w-full rounded-xl border bg-black"
            />
          </div>
        )}
      </div>

      {isReady && (
        <SyncedPreviewTimeline
          videoSrc={videoUrl}
          durationSeconds={durationSeconds}
          segments={segments}
        />
      )}
    </div>
  );
}
