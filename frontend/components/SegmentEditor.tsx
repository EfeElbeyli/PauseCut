"use client";

import { useEffect, useMemo, useState } from "react";
import { updateSegments } from "@/lib/api";
import TimelineDragEditor from "@/components/TimelineDragEditor";

type Segment = {
  start: number;
  end: number;
  action: "cut" | "speedup";
  confidence: number;
  reasons: string[];
};

type Props = {
  jobId: string;
  durationSeconds?: number;
  initialSegments: Segment[];
  onSaved?: () => void;
};

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function SegmentEditor({
  jobId,
  durationSeconds,
  initialSegments,
  onSaved,
}: Props) {
  const [segments, setSegments] = useState<Segment[]>(initialSegments);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setSegments(initialSegments);
  }, [initialSegments]);

  const timelineWidth = 100;
  const total = durationSeconds || 1;

  const bars = useMemo(() => {
    return segments.map((seg, idx) => ({
      idx,
      left: (seg.start / total) * timelineWidth,
      width: ((seg.end - seg.start) / total) * timelineWidth,
      action: seg.action,
      label: `${formatTime(seg.start)} → ${formatTime(seg.end)}`,
    }));
  }, [segments, total]);

  function updateField(index: number, field: keyof Segment, value: any) {
    const next = [...segments];
    next[index] = { ...next[index], [field]: value };
    setSegments(next);
  }

  function addSegment() {
    setSegments([
      ...segments,
      {
        start: 0,
        end: 5,
        action: "cut",
        confidence: 0.9,
        reasons: ["manual_add"],
      },
    ]);
  }

  function removeSegment(index: number) {
    setSegments(segments.filter((_, i) => i !== index));
  }

  async function saveSegments() {
    setLoading(true);
    setMessage("");
    try {
      await updateSegments(jobId, segments);
      setMessage("Segments saved. Preview cache reset.");
      onSaved?.();
    } catch (err: any) {
      setMessage(err.message || "Save failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {!!durationSeconds && (
        <TimelineDragEditor
          durationSeconds={durationSeconds}
          segments={segments}
          onChange={setSegments}
        />
      )}

      <div className="rounded-2xl border bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Manual Segment Editor</h3>
          <div className="flex gap-3">
            <button
              onClick={addSegment}
              className="rounded-xl border px-4 py-2 text-sm font-medium"
            >
              Add segment
            </button>
            <button
              onClick={saveSegments}
              disabled={loading}
              className="rounded-xl bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              {loading ? "Saving..." : "Save changes"}
            </button>
          </div>
        </div>

        <div className="mb-6 rounded-xl border p-4">
          <div className="mb-3 text-sm text-gray-600">Timeline preview</div>
          <div className="relative h-12 rounded-xl bg-gray-100">
            {bars.map((bar) => (
              <div
                key={bar.idx}
                title={bar.label}
                className={`absolute top-2 h-8 rounded-lg ${
                  bar.action === "cut" ? "bg-red-400" : "bg-amber-400"
                }`}
                style={{
                  left: `${bar.left}%`,
                  width: `${Math.max(bar.width, 1)}%`,
                }}
              />
            ))}
          </div>
          <div className="mt-2 flex justify-between text-xs text-gray-500">
            <span>0:00</span>
            <span>{formatTime(total)}</span>
          </div>
        </div>

        <div className="space-y-4">
          {segments.length === 0 && (
            <p className="text-sm text-gray-500">No editable segments yet.</p>
          )}

          {segments.map((seg, idx) => (
            <div key={idx} className="grid grid-cols-5 gap-3 rounded-xl border p-4">
              <div>
                <label className="mb-1 block text-xs text-gray-500">Start</label>
                <input
                  type="number"
                  step="0.1"
                  value={seg.start}
                  onChange={(e) => updateField(idx, "start", Number(e.target.value))}
                  className="w-full rounded-lg border px-3 py-2"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs text-gray-500">End</label>
                <input
                  type="number"
                  step="0.1"
                  value={seg.end}
                  onChange={(e) => updateField(idx, "end", Number(e.target.value))}
                  className="w-full rounded-lg border px-3 py-2"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs text-gray-500">Action</label>
                <select
                  value={seg.action}
                  onChange={(e) => updateField(idx, "action", e.target.value as "cut" | "speedup")}
                  className="w-full rounded-lg border px-3 py-2"
                >
                  <option value="cut">cut</option>
                  <option value="speedup">speedup</option>
                </select>
              </div>

              <div>
                <label className="mb-1 block text-xs text-gray-500">Confidence</label>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={seg.confidence}
                  onChange={(e) => updateField(idx, "confidence", Number(e.target.value))}
                  className="w-full rounded-lg border px-3 py-2"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => removeSegment(idx)}
                  className="w-full rounded-lg border px-3 py-2 text-sm"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>

        {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
      </div>
    </div>
  );
}
