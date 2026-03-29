type Segment = {
  start: number;
  end: number;
  action: "cut" | "speedup";
  confidence: number;
  reasons: string[];
};

type Props = {
  segments: Segment[];
};

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function SegmentList({ segments }: Props) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Suggested segments</h3>

      <div className="space-y-4">
        {segments.length === 0 && (
          <p className="text-sm text-gray-500">No segments yet.</p>
        )}

        {segments.map((segment, i) => (
          <div key={i} className="rounded-xl border p-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="font-medium">
                {formatTime(segment.start)} → {formatTime(segment.end)}
              </p>
              <span className="rounded-full border px-3 py-1 text-sm">{segment.action}</span>
            </div>

            <p className="mb-2 text-sm text-gray-600">
              Confidence: {Math.round(segment.confidence * 100)}%
            </p>

            <div className="flex flex-wrap gap-2">
              {segment.reasons.map((reason, idx) => (
                <span key={idx} className="rounded-full bg-gray-100 px-3 py-1 text-xs">
                  {reason}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
