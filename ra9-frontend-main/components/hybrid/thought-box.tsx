"use client"

type AgentName = "logical" | "creative" | "strategic" | "reflective"

export type ThoughtBoxProps = {
  agentName: AgentName
  streaming: boolean
  latestTokens?: string[]
  confidence: number // 0..100
  onFocus: () => void
}

const NAME_LABEL: Record<AgentName, string> = {
  logical: "Logical",
  creative: "Creative",
  strategic: "Strategic",
  reflective: "Reflective",
}

export function ThoughtBox(props: ThoughtBoxProps) {
  const { agentName, streaming, latestTokens = [], confidence, onFocus } = props
  const text = latestTokens.slice(-8).join(" ")
  const confWidth = Math.max(0, Math.min(100, confidence))

  return (
    <button
      onClick={onFocus}
      className="w-44 h-12 rounded-md p-2 bg-foreground/5 hover:bg-foreground/10 transition-colors flex items-center gap-2 text-left"
      aria-live="polite"
      aria-label={`${NAME_LABEL[agentName]} agent thought`}
    >
      {/* confidence bar (compact) */}
      <div className="w-10 h-1.5 rounded-full bg-foreground/10" aria-hidden>
        <div className="h-1.5 rounded-full bg-[color:var(--ra9-primary)]" style={{ width: `${confWidth}%` }} />
      </div>
      <div className="text-xs font-semibold">{NAME_LABEL[agentName]}</div>
      <div className="flex-1 text-sm truncate">{streaming ? text || "…" : text}</div>
    </button>
  )
}
