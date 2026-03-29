function getApiBase() {
  if (process.env.NEXT_PUBLIC_API_BASE) {
    return process.env.NEXT_PUBLIC_API_BASE;
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;

    if (host === "localhost" || host === "127.0.0.1") {
      return "http://localhost:8000";
    }

    return `${window.location.protocol}//${host}:8000`;
  }

  return "http://localhost:8000";
}

const API_BASE = getApiBase();

export async function analyzeLink(payload: {
  url: string;
  mode: "cut" | "smart";
  protect_dialogue: boolean;
  preview_only: boolean;
}) {
  const res = await fetch(`${API_BASE}/analyze-link`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || "Analysis request failed");
  }

  return res.json();
}

export async function getJobSummary(jobId: string) {
  const res = await fetch(`${API_BASE}/job/${jobId}/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch job summary");
  return res.json();
}

export async function getSegments(jobId: string) {
  const res = await fetch(`${API_BASE}/job/${jobId}/segments`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch segments");
  return res.json();
}

export async function updateSegments(jobId: string, segments: any[]) {
  const res = await fetch(`${API_BASE}/job/${jobId}/segments`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(segments),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Failed to update segments");
  return data;
}

export async function buildPreview(jobIdWithQuery: string) {
  const res = await fetch(`${API_BASE}/job/${jobIdWithQuery}/preview`, {
    method: "POST",
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Preview render failed");
  return data;
}

export async function buildFinal(jobIdWithQuery: string) {
  const res = await fetch(`${API_BASE}/job/${jobIdWithQuery}/final`, {
    method: "POST",
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Final render failed");
  return data;
}

export function previewDownloadUrl(jobId: string) {
  return `${API_BASE}/job/${jobId}/preview/download`;
}

export function finalDownloadUrl(jobId: string) {
  return `${API_BASE}/job/${jobId}/final/download`;
}
