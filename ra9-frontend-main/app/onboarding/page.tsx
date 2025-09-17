export default function OnboardingPage() {
  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">Welcome to RA9</h1>
        <p className="text-sm text-muted-foreground">A quick tour of key concepts.</p>
      </header>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <article className="ra9-card p-4">
          <h2 className="text-lg font-medium">Deliberation Dial</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Control loop depth (1–6) to balance speed and thoroughness.
          </p>
        </article>
        <article className="ra9-card p-4">
          <h2 className="text-lg font-medium">Thought Trace</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Inspect each iteration’s changes and confidence over time.
          </p>
        </article>
        <article className="ra9-card p-4">
          <h2 className="text-lg font-medium">Memory Consent</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Memory writes are opt-in per query. Approve or redact in Memory Browser.
          </p>
        </article>
        <article className="ra9-card p-4">
          <h2 className="text-lg font-medium">Tool Sandbox</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Dry-run tools with preflight checks before executing actions.
          </p>
        </article>
      </section>
    </main>
  )
}
