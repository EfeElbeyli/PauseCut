import LinkForm from "@/components/LinkForm";

export default function HomePage() {
  return (
    <main className="space-y-8">
      <section className="space-y-3">
        <h1 className="text-4xl font-bold">PauseCut</h1>
        <p className="max-w-2xl text-gray-600">
          Audio-first pause trimming for YouTube videos. Fast analysis first, then either aggressive cuts
          or smarter cut-plus-speed edits without the old frame-analysis slowdown.
        </p>
      </section>

      <LinkForm />
    </main>
  );
}
