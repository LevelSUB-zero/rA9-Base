"use client"

export type Iteration = {
  iterationIndex: number
  timestamp: string
  agentOutputs: { agentName: string; text: string; confidence: number; tokensRef?: string }[]
  memoryHits: { id: string; score: number }[]
  citations: { source: string; url: string }[]
  verifier: { passed: boolean; score?: number; notes?: string[] }
  deltaSummary: string
}

export default function HybridIterationTimeline({
  iterations,
  onSelect,
}: {
  iterations: Iteration[]
  onSelect: (i: number) => void
}) {
  return (
    <div>
      <div className="text-sm font-medium mb-2">Iterations</div>
      <ol className="space-y-2">
        {iterations.map((it) => (
          <li key={it.iterationIndex}>
            <button
              className="w-full text-left rounded-lg border border-border bg-card p-2 hover:bg-muted"
              onClick={() => onSelect(it.iterationIndex)}
              aria-describedby={`delta-${it.iterationIndex}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-0.5 rounded-full border border-border">#{it.iterationIndex}</span>
                  <span className="text-xs text-muted-foreground">{new Date(it.timestamp).toLocaleTimeString()}</span>
                </div>
                <span
                  className={`w-2 h-2 rounded-full ${it.verifier?.passed ? "bg-primary" : "bg-destructive"}`}
                  aria-label={it.verifier?.passed ? "Verified" : "Failed verification"}
                  title={it.verifier?.passed ? "Verified" : "Failed verification"}
                />
              </div>
              <div id={`delta-${it.iterationIndex}`} className="mt-1 text-sm text-pretty">
                {it.deltaSummary}
              </div>
            </button>
          </li>
        ))}
        {iterations.length === 0 && <li className="text-sm text-muted-foreground">No iterations yet.</li>}
      </ol>
    </div>
  )
}
