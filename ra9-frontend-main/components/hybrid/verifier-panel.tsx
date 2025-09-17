"use client"

export function VerifierPanel({ result }: { result: { passed: boolean; score: number; notes: string[] } }) {
  const color = result.passed ? "var(--ra9-primary)" : "var(--ra9-accent)"
  return (
    <div className="border rounded-lg p-3 bg-background/60">
      <div className="text-sm font-semibold" style={{ color }}>
        {result.passed ? "Verifier: Passed" : "Verifier: Failed"}
      </div>
      <div className="text-xs opacity-80">Score: {Math.round(result.score * 100)}%</div>
      <ul className="mt-2 list-disc list-inside text-xs">
        {result.notes.map((n, i) => (
          <li key={i}>{n}</li>
        ))}
      </ul>
      {!result.passed ? (
        <div className="mt-2">
          <button className="px-3 py-1 rounded bg-foreground/10 hover:bg-foreground/20 text-xs">
            Request Human Review
          </button>
        </div>
      ) : null}
    </div>
  )
}
