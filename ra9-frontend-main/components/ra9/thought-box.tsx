"use client"

type AgentName = "logical" | "creative" | "strategic" | "reflective"

export default function ThoughtBox(props: {
  agentName: AgentName
  streaming: boolean
  latestTokens?: string[]
  confidence: number // 0..100
  onFocus: () => void
}) {
  const { agentName, streaming, latestTokens = [], confidence, onFocus } = props
  const label = agentName[0].toUpperCase() + agentName.slice(1)

  const preview = latestTokens.slice(-6).join(" ")
  const barWidth = Math.max(2, Math.min(100, Math.round(confidence))) // 2..100

  return (
    <button
      type="button"
      onClick={onFocus}
      className="w-44 h-12 rounded-md p-2 bg-card border border-border flex items-center gap-2 overflow-hidden text-left"
      aria-live="polite"
      title={`Focus ${label} agent`}
    >
      <div className="w-1.5 h-full rounded bg-primary" style={{ width: 4 }} aria-hidden />
      <div className="text-xs font-semibold">{label}</div>
      <div className="flex-1 text-xs md:text-sm truncate">{preview || (streaming ? "…" : "")}</div>
      <div className="w-10">
        <div className="h-1.5 rounded-full bg-muted" aria-hidden>
          <div className="h-1.5 rounded-full bg-primary" style={{ width: `${barWidth}%` }} />
        </div>
      </div>
    </button>
  )
}
