type Props = {
  summary: {
    title?: string;
    platform?: string;
    duration_seconds?: number;
    estimated_time_saved_seconds?: number;
    mode: string;
    status: string;
    progress: number;
    protect_dialogue: boolean;
    preview_only: boolean;
    segments_found?: number;
    error_message?: string | null;
  };
};

function formatSeconds(total?: number) {
  if (total === undefined || total === null) return "-";
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}m ${seconds}s`;
}

function humanMode(mode: string) {
  if (mode === "cut") return "Cut Mode";
  if (mode === "smart") return "Smart Mode";
  return mode;
}

export default function JobSummaryCard({ summary }: Props) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold">{summary.title || "Untitled video"}</h2>

      <div className="mb-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span>Progress</span>
          <span>{summary.progress}%</span>
        </div>
        <div className="h-3 w-full rounded-full bg-gray-100">
          <div className="h-3 rounded-full bg-black transition-all" style={{ width: `${summary.progress}%` }} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div><p className="text-gray-500">Platform</p><p>{summary.platform || "-"}</p></div>
        <div><p className="text-gray-500">Status</p><p>{summary.status}</p></div>
        <div><p className="text-gray-500">Original duration</p><p>{formatSeconds(summary.duration_seconds)}</p></div>
        <div><p className="text-gray-500">Estimated saved</p><p>{formatSeconds(summary.estimated_time_saved_seconds)}</p></div>
        <div><p className="text-gray-500">Segments found</p><p>{summary.segments_found ?? "-"}</p></div>
        <div><p className="text-gray-500">Mode</p><p>{humanMode(summary.mode)}</p></div>
      </div>

      {summary.error_message && <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">{summary.error_message}</p>}
    </div>
  );
}
