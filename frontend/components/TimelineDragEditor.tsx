"use client";

type Segment = {
  start: number;
  end: number;
  action: "cut" | "speedup";
  confidence: number;
  reasons: string[];
};

type Props = {
  durationSeconds: number;
  segments: Segment[];
  onChange: (segments: Segment[]) => void;
};

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function TimelineDragEditor({
  durationSeconds,
  segments,
  onChange,
}: Props) {
  function setStart(index: number, value: number) {
    const next = [...segments];
    next[index] = {
      ...next[index],
      start: Math.max(0, Math.min(value, next[index].end - 0.2)),
    };
    onChange(next);
  }

  function setEnd(index: number, value: number) {
    const next = [...segments];
    next[index] = {
      ...next[index],
      end: Math.min(durationSeconds, Math.max(value, next[index].start + 0.2)),
    };
    onChange(next);
  }

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Drag Timeline Editor</h3>

      <div className="space-y-6">
        {segments.length === 0 && (
          <p className="text-sm text-gray-500">No timeline segments to drag.</p>
        )}

        {segments.map((seg, idx) => {
          const left = (seg.start / durationSeconds) * 100;
          const width = ((seg.end - seg.start) / durationSeconds) * 100;

          return (
            <div key={idx} className="rounded-xl border p-4">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-sm font-medium">
                  Segment {idx + 1} — {seg.action}
                </span>
                <span className="text-xs text-gray-500">
                  {formatTime(seg.start)} → {formatTime(seg.end)}
                </span>
              </div>

              <div className="relative mb-4 h-10 rounded-xl bg-gray-100">
                <div
                  className={`absolute top-1 h-8 rounded-lg ${
                    seg.action === "cut" ? "bg-red-400/80" : "bg-amber-400/80"
                  }`}
                  style={{
                    left: `${left}%`,
                    width: `${Math.max(width, 1)}%`,
                  }}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-2 block text-xs text-gray-500">
                    Start ({seg.start.toFixed(1)}s)
                  </label>
                  <input
                    type="range"
                    min={0}
                    max={durationSeconds}
                    step={0.1}
                    value={seg.start}
                    onChange={(e) => setStart(idx, Number(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-xs text-gray-500">
                    End ({seg.end.toFixed(1)}s)
                  </label>
                  <input
                    type="range"
                    min={0}
                    max={durationSeconds}
                    step={0.1}
                    value={seg.end}
                    onChange={(e) => setEnd(idx, Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
