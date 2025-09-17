"use client"

import { useEffect, useState } from "react"
import type { JobId, Message, QueryRequest, Iteration } from "@/types/hybrid"
import { HybridComposer } from "@/components/hybrid/hybrid-composer"
import { HybridChatStream } from "@/components/hybrid/hybrid-chat-stream"
import { IterationTimeline } from "@/components/hybrid/iteration-timeline"
import { VerifierPanel } from "@/components/hybrid/verifier-panel"
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function HybridWorkspacePage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [liveJob, setLiveJob] = useState<JobId | undefined>(undefined)
  const [selectedIteration, setSelectedIteration] = useState<number | null>(null)

  // Replace the most recent RA9 placeholder with final streamed text
  useEffect(() => {
    function onFinalText(ev: Event) {
      const { text, iterations } = (ev as CustomEvent).detail as { text: string; iterations: number }
      setMessages((prev) => {
        const idx = [...prev].reverse().findIndex((m) => m.role === "ra9")
        if (idx === -1) return prev
        const realIdx = prev.length - 1 - idx
        const updated = [...prev]
        updated[realIdx] = {
          ...updated[realIdx],
          content: text.trim() || updated[realIdx].content,
          meta: { ...(updated[realIdx].meta || {}), iterations },
        }
        return updated
      })
    }
    window.addEventListener("ra9-final-text", onFinalText as EventListener)
    return () => window.removeEventListener("ra9-final-text", onFinalText as EventListener)
  }, [])

  // when an iteration is selected, fetch its trace (using live or demo job id)
  const activeJobId = liveJob ?? "demo-job"
  const { data: trace } = useSWR<{ jobId: string; iterations: Iteration[] }>(
    selectedIteration != null ? `/api/v1/trace/${encodeURIComponent(activeJobId)}` : null,
    fetcher,
  )

  async function handleSubmit(req: QueryRequest): Promise<JobId> {
    // Align body with existing app/page.tsx usage for compatibility
    const res = await fetch("/api/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: req.text,
        mode: req.mode,
        memoryWrite: req.allowMemoryWrite,
        userId: req.userId,
        meta: { loopDepth: req.loopDepth },
      }),
    })
    const json = await res.json()
    const jobId: JobId = json.jobId
    setLiveJob(jobId)

    // Add user question and placeholder RA9 message
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: req.text },
      {
        id: crypto.randomUUID(),
        role: "ra9",
        content: "Thinking…",
        meta: { loopDepth: req.loopDepth, iterations: 0, confidenceAvg: 0.5 },
      },
    ])

    return jobId
  }

  // Layout: xl -> 3 columns (3/6/3), md -> 2 columns (center+right), base -> single
  return (
    <main className="p-4 md:p-6">
      <div className="grid gap-4 grid-cols-1 md:grid-cols-6 xl:grid-cols-12">
        {/* Left column: Sessions / Memory filters (xl only) */}
        <aside className="hidden xl:block xl:col-span-3">
          <div className="border rounded-lg p-3 bg-background/60 backdrop-blur">
            <div className="text-sm font-semibold mb-2">Sessions</div>
            <ul className="space-y-1 text-sm">
              <li>
                <button className="w-full text-left hover:underline">Today • Research</button>
              </li>
              <li>
                <button className="w-full text-left hover:underline">Bug triage</button>
              </li>
              <li>
                <button className="w-full text-left hover:underline">Notes</button>
              </li>
            </ul>
            <div className="mt-4 text-sm font-semibold">Memory quick filters</div>
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="px-2 py-1 rounded bg-foreground/10 text-xs">recent</span>
              <span className="px-2 py-1 rounded bg-foreground/10 text-xs">high-confidence</span>
              <span className="px-2 py-1 rounded bg-foreground/10 text-xs">requires-review</span>
            </div>
            <div className="mt-4 text-sm">
              Shortcuts:
              <ul className="list-disc list-inside text-xs mt-1">
                <li>Ctrl+K focus composer</li>
                <li>Ctrl+Enter send</li>
                <li>Ctrl+[ / Ctrl+] iteration nav</li>
              </ul>
            </div>
          </div>
        </aside>

        {/* Center column: Composer + Chat */}
        <section className="md:col-span-4 xl:col-span-6">
          <HybridComposer userId="user_1" onSubmit={handleSubmit} defaultLoopDepth={2} initialMode="concise" />
          <div className="mt-4">
            <HybridChatStream
              sessionId="session_1"
              messages={messages}
              liveJob={liveJob}
              onInspectIteration={(i) => setSelectedIteration(Number(i))}
            />
          </div>
        </section>

        {/* Right column: Inspector */}
        <aside className="md:col-span-2 xl:col-span-3">
          <div className="space-y-4">
            <div className="border rounded-lg p-3 bg-background/60 backdrop-blur">
              <div className="text-sm font-semibold mb-2">Iteration Timeline</div>
              <IterationTimeline
                iterations={trace?.iterations ?? demoIterations}
                onSelect={(i) => setSelectedIteration(i)}
              />
            </div>
            <VerifierPanel
              result={{ passed: true, score: 0.91, notes: ["Citations validated", "Claims internally consistent"] }}
            />
          </div>
        </aside>
      </div>
    </main>
  )
}

const demoIterations: Iteration[] = [
  {
    iterationIndex: 0,
    timestamp: new Date().toISOString(),
    agentOutputs: [
      { agentName: "logical", text: "Outlined the key claims and premises.", confidence: 0.78 },
      { agentName: "creative", text: "Proposed alternative framing and analogy.", confidence: 0.44 },
    ],
    memoryHits: [{ id: "m_123", score: 0.83 }],
    citations: [{ source: "arXiv", url: "https://arxiv.org" }],
    verifier: { passed: true, score: 0.91, notes: [] },
    deltaSummary: "Refined claim X→Y; removed speculative paragraph.",
  },
]
