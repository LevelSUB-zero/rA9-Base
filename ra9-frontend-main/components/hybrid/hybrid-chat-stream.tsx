"use client"

import { useEffect, useRef, useState } from "react"
import type { HybridChatStreamProps } from "@/types/hybrid"
import { ThoughtBox } from "./thought-box"

type AgentName = "logical" | "creative" | "strategic" | "reflective" | "actor" | "system"

type LiveState = {
  iteration: number
  agents: Record<AgentName, { tokens: string[]; confidence: number }>
}

const DEFAULT_LIVE: LiveState = {
  iteration: 0,
  agents: {
    logical: { tokens: [], confidence: 70 },
    creative: { tokens: [], confidence: 50 },
    strategic: { tokens: [], confidence: 60 },
    reflective: { tokens: [], confidence: 55 },
    actor: { tokens: [], confidence: 80 },
    system: { tokens: [], confidence: 90 },
  },
}

export function HybridChatStream(props: HybridChatStreamProps) {
  const { messages, liveJob, onInspectIteration } = props
  const [live, setLive] = useState<LiveState>(DEFAULT_LIVE)
  const esRef = useRef<EventSource | null>(null)
  const finalTextRef = useRef<string>("")
  const iterationsRef = useRef<number>(0)

  // Connect SSE when liveJob present
  useEffect(() => {
    if (!liveJob) return
    const url = `/api/v1/job/${encodeURIComponent(liveJob)}/stream`
    const es = new EventSource(url)
    esRef.current = es
    finalTextRef.current = ""
    iterationsRef.current = 0

    es.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        if (data.type === "token") {
          const agent = data.agent as AgentName
          const token: string = data.text
          if (agent === "actor") {
            finalTextRef.current += token
          }
          setLive((prev) => ({
            ...prev,
            iteration: data.iteration ?? prev.iteration,
            agents: {
              ...prev.agents,
              [agent]: {
                ...(prev.agents[agent] || { tokens: [], confidence: 70 }),
                tokens: [...(prev.agents[agent]?.tokens || []), token],
              },
            },
          }))
        } else if (data.type === "iteration_complete") {
          const step: number = data?.iteration?.step ?? data?.iteration?.iterationIndex ?? 0
          iterationsRef.current = step || iterationsRef.current
          setLive((prev) => ({
            ...prev,
            iteration: step || prev.iteration,
          }))
        } else if (data.type === "done") {
          // Notify parent via browser event to replace the placeholder message
          window.dispatchEvent(
            new CustomEvent("ra9-final-text", {
              detail: { text: finalTextRef.current, iterations: iterationsRef.current },
            }),
          )
          es.close()
        }
      } catch (e) {
        console.error("[v0] SSE parse error", e)
      }
    }

    es.onerror = () => {
      console.error("[v0] SSE error")
      es.close()
    }

    return () => es.close()
  }, [liveJob])

  useEffect(() => {
    if (!liveJob) setLive(DEFAULT_LIVE)
  }, [liveJob])

  return (
    <div className="space-y-4">
      {/* ThoughtBoxes strip */}
      {liveJob ? (
        <div className="flex gap-2">
          {(Object.keys(live.agents) as AgentName[]).map((agent) => (
            <ThoughtBox
              key={agent}
              agentName={agent}
              streaming={true}
              latestTokens={live.agents[agent].tokens}
              confidence={live.agents[agent].confidence}
              onFocus={() => onInspectIteration(String(live.iteration))}
            />
          ))}
        </div>
      ) : null}

      {/* Chat messages */}
      <div className="space-y-3">
        {messages.map((m) => (
          <div key={m.id} className="bg-foreground/5 rounded-lg p-3">
            <div className="text-xs opacity-70 mb-1">{m.role === "user" ? "You" : "RA9"}</div>
            <div className="text-sm text-pretty">{m.content}</div>
            {m.role === "ra9" && m.meta ? (
              <div className="flex items-center gap-3 mt-2 text-xs opacity-80">
                {m.meta.loopDepth != null && <span>depth: {m.meta.loopDepth}</span>}
                {m.meta.confidenceAvg != null && <span>conf: {Math.round((m.meta.confidenceAvg || 0) * 100)}%</span>}
                {m.meta.iterations != null && <span>iters: {m.meta.iterations}</span>}
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  )
}
