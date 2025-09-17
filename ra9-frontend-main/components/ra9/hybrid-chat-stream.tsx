"use client"

import { useEffect, useState } from "react"
import ThoughtBox from "@/components/ra9/thought-box"

export type Message = {
  id: string
  role: "user" | "assistant"
  content: string
  meta?: Record<string, any>
}

export type Iteration = {
  iterationIndex: number
  timestamp: string
  agentOutputs: { agentName: string; text: string; confidence: number; tokensRef?: string }[]
  memoryHits: { id: string; score: number }[]
  citations: { source: string; url: string }[]
  verifier: { passed: boolean; score?: number; notes?: string[] }
  deltaSummary: string
}

export type HybridChatStreamProps = {
  sessionId: string
  messages: Message[]
  liveJob?: string
  onAssistantMessage?: (content: string, meta?: Record<string, any>) => void
  onIterationComplete?: (iteration: Iteration) => void
  onInspectIteration: (iterationId: string) => void
}

const AGENTS = ["logical", "creative", "strategic", "reflective"] as const
type AgentName = (typeof AGENTS)[number]

type AgentState = {
  tokens: string[]
  confidence: number
}

export default function HybridChatStream(props: HybridChatStreamProps) {
  const { sessionId, messages, liveJob, onAssistantMessage, onIterationComplete, onInspectIteration } = props

  const [agentState, setAgentState] = useState<Record<AgentName, AgentState>>({
    logical: { tokens: [], confidence: 72 },
    creative: { tokens: [], confidence: 48 },
    strategic: { tokens: [], confidence: 61 },
    reflective: { tokens: [], confidence: 55 },
  })

  // SSE subscription (fallback to mock stream if API not available)
  useEffect(() => {
    if (!liveJob) return

    let closed = false
    let es: EventSource | null = null
    try {
      es = new EventSource(`/api/v1/job/${liveJob}/stream`)
      es.onmessage = (ev) => {
        if (closed) return
        try {
          const data = JSON.parse(ev.data)
          if (data.type === "token") {
            const agent = (data.agent || "logical") as AgentName
            const token = data.text as string
            setAgentState((prev) => ({
              ...prev,
              [agent]: {
                ...prev[agent],
                tokens: [...prev[agent].tokens, token].slice(-40), // keep recent window
              },
            }))
          } else if (data.type === "iteration_complete") {
            const it: Iteration = {
              iterationIndex: Number(data.iteration ?? 0),
              timestamp: new Date().toISOString(),
              agentOutputs: AGENTS.map((a) => ({
                agentName: a,
                text: agentState[a].tokens.join(" "),
                confidence: agentState[a].confidence / 100,
              })),
              memoryHits: [],
              citations: [],
              verifier: data.verifier ?? { passed: true, score: 0.9, notes: [] },
              deltaSummary: "Refined reasoning based on latest evidence.",
            }
            onIterationComplete?.(it)
            // also append assistant message from combined tokens
            const combined = AGENTS.map((a) => agentState[a].tokens.join(" ")).join(" ")
            onAssistantMessage?.(combined, { loopDepth: data.loopDepth ?? 1, iterationIndex: it.iterationIndex })
            // reset tokens for next iteration
            setAgentState((prev) => {
              const next: Record<AgentName, AgentState> = { ...prev }
              AGENTS.forEach((a) => (next[a] = { ...next[a], tokens: [] }))
              return next
            })
          }
        } catch {
          // ignore parse errors
        }
      }
      es.onerror = () => {
        // If SSE fails, fall back to local simulation
        if (!closed) {
          es?.close()
          simulateLocalStream(liveJob)
        }
      }
    } catch {
      simulateLocalStream(liveJob)
    }
    return () => {
      closed = true
      es?.close()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [liveJob])

  const simulateLocalStream = (jobId: string) => {
    // very small mock typewriter across agents
    const words = [
      "Thinking",
      "about",
      "the",
      "question,",
      "evaluating",
      "evidence",
      "and",
      "forming",
      "a",
      "response.",
    ]
    let i = 0
    const timer = setInterval(() => {
      const agent = AGENTS[i % AGENTS.length]
      const token = words[i % words.length]
      setAgentState((prev) => ({
        ...prev,
        [agent]: { ...prev[agent], tokens: [...prev[agent].tokens, token].slice(-40) },
      }))
      i++
      if (i > words.length * 2) {
        clearInterval(timer)
        const it: Iteration = {
          iterationIndex: 0,
          timestamp: new Date().toISOString(),
          agentOutputs: AGENTS.map((a) => ({
            agentName: a,
            text: agentState[a].tokens.join(" "),
            confidence: agentState[a].confidence / 100,
          })),
          memoryHits: [],
          citations: [],
          verifier: { passed: true, score: 0.9, notes: [] },
          deltaSummary: "Generated draft answer.",
        }
        onIterationComplete?.(it)
        const combined = AGENTS.map((a) => agentState[a].tokens.join(" ")).join(" ")
        onAssistantMessage?.(combined, { loopDepth: 1, iterationIndex: it.iterationIndex })
        // reset
        setAgentState((prev) => {
          const next: Record<AgentName, AgentState> = { ...prev }
          AGENTS.forEach((a) => (next[a] = { ...next[a], tokens: [] }))
          return next
        })
      }
    }, 80)
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Thought strip above most recent assistant message */}
      <div className="flex flex-wrap gap-2">
        {AGENTS.map((a) => (
          <ThoughtBox
            key={a}
            agentName={a as AgentName}
            streaming={Boolean(liveJob)}
            latestTokens={agentState[a as AgentName].tokens}
            confidence={agentState[a as AgentName].confidence}
            onFocus={() => onInspectIteration("0")}
          />
        ))}
      </div>

      {/* Messages */}
      <div className="space-y-3">
        {messages.map((m) => (
          <div
            key={m.id}
            className={m.role === "user" ? "rounded-lg p-3 bg-card border border-border" : "rounded-lg p-3 bg-muted"}
            aria-label={m.role === "user" ? "User message" : "RA9 message"}
          >
            {m.role === "assistant" && (
              <div className="mb-1 flex items-center gap-2 text-xs text-muted-foreground">
                <span className="px-2 py-0.5 rounded-full border border-border">loop {m.meta?.loopDepth ?? 1}</span>
                <span className="px-2 py-0.5 rounded-full border border-border">
                  iterations {m.meta?.iterationIndex != null ? m.meta.iterationIndex + 1 : 1}
                </span>
              </div>
            )}
            <div className="text-sm leading-relaxed whitespace-pre-wrap">{m.content}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
