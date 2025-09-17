"use client"
import { cn } from "@/lib/utils"

export type Iteration = {
  id: string
  index: number
  summary: string
  confidence: number
  timestamp: string
}

export function IterationTimeline({
  iterations,
  className,
}: {
  iterations: Iteration[]
  className?: string
}) {
  return (
    <ol
      className={cn(
        "relative space-y-4 before:absolute before:left-4 before:top-0 before:h-full before:w-px before:bg-[color:var(--ra9-border)]",
        className,
      )}
      aria-label="Iteration timeline"
    >
      {iterations.map((it) => (
        <li key={it.id} className="relative pl-10">
          <span
            className="absolute left-2 top-2 h-4 w-4 rounded-full"
            style={{ background: "var(--ra9-primary)" }}
            aria-hidden
          />
          <div
            className="rounded-xl border p-3"
            style={{
              borderColor: "var(--ra9-border)",
              background: "var(--ra9-surface-1)",
              backdropFilter: "blur(8px)",
            }}
          >
            <div className="flex items-center justify-between">
              <div className="text-sm">
                <span className="text-muted-foreground">Iteration</span> <strong>#{it.index}</strong>
              </div>
              <div className="text-xs text-muted-foreground">{new Date(it.timestamp).toLocaleTimeString()}</div>
            </div>
            <p className="mt-2 text-sm leading-relaxed">{it.summary}</p>
            <div className="mt-2 flex items-center gap-2">
              <ConfidenceBar value={it.confidence} />
              <button
                type="button"
                className="ml-auto text-xs text-[color:var(--ra9-accent)] underline-offset-2 hover:underline"
                aria-label={`Inspect details for iteration ${it.index}`}
                onClick={() => console.log("[v0] Inspect iteration", it)}
              >
                Inspect
              </button>
            </div>
          </div>
        </li>
      ))}
    </ol>
  )
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100)
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-28 overflow-hidden rounded-full border" style={{ borderColor: "var(--ra9-border)" }}>
        <div
          className="h-full"
          style={{
            width: `${pct}%`,
            background: "var(--ra9-primary)",
            transition: "width var(--ra9-motion-medium) var(--ra9-ease-standard)",
          }}
          aria-hidden
        />
      </div>
      <span className="text-xs text-muted-foreground">{pct}%</span>
    </div>
  )
}
