"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeLink } from "@/lib/api";

export default function LinkForm() {
  const router = useRouter();

  const [url, setUrl] = useState("");
  const [mode, setMode] = useState<"cut" | "smart">("smart");
  const [protectDialogue, setProtectDialogue] = useState(true);
  const [previewOnly, setPreviewOnly] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const job = await analyzeLink({
        url,
        mode,
        protect_dialogue: protectDialogue,
        preview_only: previewOnly,
      });
      router.push(`/result/${job.job_id}`);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-2xl border bg-white p-6 shadow-sm">
      <div>
        <label className="mb-2 block text-sm font-medium">YouTube Link</label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          className="w-full rounded-xl border px-4 py-3 outline-none"
          required
        />
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium">Edit Mode</label>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value as "cut" | "smart")}
          className="w-full rounded-xl border px-4 py-3"
        >
          <option value="cut">Cut Mode — aggressive shortening</option>
          <option value="smart">Smart Mode — cut long pauses, speed short ones</option>
        </select>
      </div>

      <div className="rounded-xl bg-gray-50 p-4 text-sm text-gray-700">
        {mode === "cut"
          ? "Cut Mode removes detected dead air aggressively for maximum shortening."
          : "Smart Mode cuts long silent gaps and speeds through shorter pauses to preserve visual flow."}
      </div>

      <label className="flex items-center gap-3">
        <input type="checkbox" checked={protectDialogue} onChange={(e) => setProtectDialogue(e.target.checked)} />
        <span>Protect dialogue with VAD check</span>
      </label>

      <label className="flex items-center gap-3">
        <input type="checkbox" checked={previewOnly} onChange={(e) => setPreviewOnly(e.target.checked)} />
        <span>Preview only</span>
      </label>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-black px-4 py-3 font-medium text-white disabled:opacity-60"
      >
        {loading ? "Submitting..." : "Analyze video"}
      </button>
    </form>
  );
}
