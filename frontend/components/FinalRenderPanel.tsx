"use client";

import { useState } from "react";
import { buildFinal, finalDownloadUrl } from "@/lib/api";

type Props = {
  jobId: string;
  jobStatus: string;
  finalStatus?: string;
  finalError?: string | null;
};

export default function FinalRenderPanel({
  jobId,
  jobStatus,
  finalStatus,
  finalError,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [finalReady, setFinalReady] = useState(finalStatus === "ready");
  const [error, setError] = useState("");

  async function handleBuildFinal(force = false) {
    setLoading(true);
    setError("");

    try {
      await buildFinal(jobId + (force ? "?force=true" : ""));
      setFinalReady(true);
    } catch (err: any) {
      setError(err.message || "Final render failed");
    } finally {
      setLoading(false);
    }
  }

  const downloadUrl = finalDownloadUrl(jobId);

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Export Final Video</h3>

      {jobStatus !== "completed" ? (
        <p className="text-sm text-gray-500">
          Final export can be built after analysis finishes.
        </p>
      ) : (
        <>
          <div className="mb-4 flex flex-wrap gap-3">
            <button
              onClick={() => handleBuildFinal(false)}
              disabled={loading}
              className="rounded-xl bg-black px-4 py-3 text-sm font-medium text-white disabled:opacity-60"
            >
              {loading ? "Rendering final..." : "Build final video"}
            </button>

            <button
              onClick={() => handleBuildFinal(true)}
              disabled={loading}
              className="rounded-xl border px-4 py-3 text-sm font-medium disabled:opacity-60"
            >
              Force rebuild
            </button>

            {finalReady && (
              <a
                href={downloadUrl}
                target="_blank"
                className="rounded-xl border px-4 py-3 text-sm font-medium"
              >
                Download final video
              </a>
            )}
          </div>

          <div className="text-sm text-gray-600">
            Final status: <span className="font-medium">{finalStatus || "not_started"}</span>
          </div>

          {(error || finalError) && (
            <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">
              {error || finalError}
            </p>
          )}
        </>
      )}
    </div>
  );
}
