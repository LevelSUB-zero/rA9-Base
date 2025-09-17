"use client"

import * as React from "react"
import { CompactTokenStreamer, type StreamToken } from "./compact-token-streamer"
import { appendBrowserMemory } from "@/lib/job-store"
import { IterationTimeline, type Iteration } from "./iteration-timeline"

type StreamEvent =
  | { type: "open"; jobId: string }
  | { type: "token"; text: string; iteration: number; kind: "verified" | "speculative" }
  | {
      type: "iteration_complete"
      iteration: number
      agentOutputs: Array<{ agent: string; content: string; confidence: number }>
    }
  | {
      type: "meta_report"
      activated_agents: string[]
      rounds: number
      primary_intent: string
      coherence_ok: boolean
      confidence_estimate: number
    }
  | { type: "done"; jobId: string }

export function StreamView({ jobId }: { jobId: string }) {
  const [tokens, setTokens] = React.useState<StreamToken[]>([])
  const [iterations, setIterations] = React.useState<Iteration[]>([])
  const finalBufferRef = React.useRef<string>("")
  const [meta, setMeta] = React.useState<{
    activated_agents: string[]
    rounds: number
    primary_intent: string
    coherence_ok: boolean
    confidence_estimate: number
  } | null>(null)

  React.useEffect(() => {
    if (!jobId) return
    console.log("[v0] Opening SSE for", jobId)
    const es = new EventSource(`/api/v1/job/${jobId}/stream`)
    es.onmessage = (ev) => {
      try {
        const data: StreamEvent = JSON.parse(ev.data)
        if (data.type === "token") {
          setTokens((prev) => [...prev, { text: data.text, kind: data.kind }])
          finalBufferRef.current += data.text
        } else if (data.type === "iteration_complete") {
          setIterations((prev) => [
            ...prev,
            {
              id: `it-${data.iteration}`,
              index: data.iteration,
              summary: data.agentOutputs.map((a) => a.content).join(" "),
              confidence:
                data.agentOutputs.reduce((acc, a) => acc + a.confidence, 0) / Math.max(1, data.agentOutputs.length),
              timestamp: new Date().toISOString(),
            },
          ])
        } else if (data.type === "meta_report") {
          setMeta({
            activated_agents: data.activated_agents,
            rounds: data.rounds,
            primary_intent: data.primary_intent,
            coherence_ok: data.coherence_ok,
            confidence_estimate: data.confidence_estimate,
          })
        } else if (data.type === "done") {
          console.log("[v0] Stream done:", data.jobId)
          // Save an episodic entry in browser cache
          const text = finalBufferRef.current.trim()
          if (text) {
            appendBrowserMemory({
              id: `ep-${Date.now()}`,
              type: "episodic",
              text,
              timestamp: new Date().toISOString(),
              tags: ["auto", "final"],
            })
          }
          es.close()
        }
      } catch (e) {
        console.log("[v0] SSE parse error", e)
      }
    }
    es.onerror = () => {
      console.log("[v0] SSE error")
      es.close()
    }
    return () => es.close()
  }, [jobId])

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div className="ra9-card p-4">
        <div className="mb-2 text-sm text-muted-foreground">Live Tokens</div>
        <CompactTokenStreamer tokens={tokens} className="text-sm leading-relaxed" />
      </div>
      <div className="ra9-card p-4">
        <div className="mb-2 text-sm text-muted-foreground">Live Iterations</div>
        <IterationTimeline iterations={iterations} />
      </div>
      {meta && (
        <div className="ra9-card p-4 md:col-span-2">
          <div className="mb-2 text-sm text-muted-foreground">Meta-Self Report</div>
          <div className="text-xs">
            <div>Agents: {meta.activated_agents.join(", ")}</div>
            <div>Rounds: {meta.rounds}</div>
            <div>Primary: {meta.primary_intent}</div>
            <div>Coherent: {meta.coherence_ok ? "yes" : "no"}</div>
            <div>Confidence: {meta.confidence_estimate.toFixed(2)}</div>
          </div>
        </div>
      )}
    </div>
  )
}
