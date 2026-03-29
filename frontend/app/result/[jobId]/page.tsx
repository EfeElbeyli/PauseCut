"use client";

import { useEffect, useState } from "react";
import JobSummaryCard from "@/components/JobSummaryCard";
import PreviewPanel from "@/components/PreviewPanel";
import ProgressWithETA from "@/components/ProgressWithETA";
import SegmentEditor from "@/components/SegmentEditor";
import SegmentList from "@/components/SegmentList";
import { getJobSummary, getSegments } from "@/lib/api";

type Props = {
  params: Promise<{ jobId: string }>;
};

function getPollInterval(summaryData: any) {
  const progress = summaryData?.progress ?? 0;
  if (progress < 20) return 1500;
  if (progress < 85) return 2500;
  if (progress < 100 || summaryData?.preview_status === "processing") return 1500;
  return null;
}

export default function ResultPage({ params }: Props) {
  const [jobId, setJobId] = useState("");
  const [summary, setSummary] = useState<any>(null);
  const [segments, setSegments] = useState<any[]>([]);
  const [error, setError] = useState("");

  async function loadJob(currentJobId: string) {
    const [summaryData, segmentData] = await Promise.all([getJobSummary(currentJobId), getSegments(currentJobId)]);
    setSummary(summaryData);
    setSegments(segmentData);
    return summaryData;
  }

  useEffect(() => {
    async function init() {
      const resolved = await params;
      setJobId(resolved.jobId);
    }
    init();
  }, [params]);

  useEffect(() => {
    if (!jobId) return;

    let timer: ReturnType<typeof setTimeout> | undefined;
    let isCancelled = false;

    async function load() {
      try {
        const summaryData = await loadJob(jobId);
        if (isCancelled) return;

        const shouldContinue =
          summaryData.status === "queued" ||
          summaryData.status === "processing" ||
          summaryData.preview_status === "processing";

        if (shouldContinue) {
          const nextInterval = getPollInterval(summaryData);
          if (nextInterval !== null) timer = setTimeout(load, nextInterval);
        }
      } catch (err: any) {
        if (!isCancelled) setError(err.message || "Failed to load result");
      }
    }

    load();
    return () => {
      isCancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [jobId]);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!summary || !jobId) return <p>Loading...</p>;

  return (
    <main className="space-y-6">
      <div>
        <h1 className="mb-2 text-3xl font-bold">Analysis result</h1>
        <p className="text-gray-600">Job ID: {jobId}</p>
      </div>

      <ProgressWithETA
        progress={summary.progress}
        stage={summary.analysis_stage}
        activityText={summary.activity_text}
        isDone={summary.status === "completed" || summary.status === "failed"}
      />
      <JobSummaryCard summary={summary} />
      <PreviewPanel
        jobId={jobId}
        jobStatus={summary.status}
        previewStatus={summary.preview_status}
        previewError={summary.preview_error}
        durationSeconds={summary.duration_seconds}
        segments={segments}
      />
      <SegmentEditor jobId={jobId} durationSeconds={summary.duration_seconds} initialSegments={segments} onSaved={() => loadJob(jobId)} />
      <SegmentList segments={segments} />
    </main>
  );
}
