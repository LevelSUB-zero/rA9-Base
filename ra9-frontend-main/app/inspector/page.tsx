"use client"

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { IterationTimeline } from "@/components/ra9/iteration-timeline"

type Trace = {
  jobId: string
  iterations: Array<{
    id: string
    iterationIndex: number
    timestamp: string
    agentOutputs: Array<{ agent: string; content: string; confidence: number }>
  }>
}

export default function InspectorPage() {
  const [jobId, setJobId] = React.useState("")
  const [iterations, setIterations] = React.useState<
    Array<{ id: string; index: number; summary: string; confidence: number; timestamp: string }>
  >([])

  async function loadTrace() {
    if (!jobId) return
    const res = await fetch(`/api/v1/trace/${jobId}`)
    const data: Trace = await res.json()
    const mapped = data.iterations.map((it) => ({
      id: it.id,
      index: it.iterationIndex,
      summary: it.agentOutputs.map((a) => a.content).join(" "),
      confidence: it.agentOutputs.reduce((acc, a) => acc + a.confidence, 0) / Math.max(1, it.agentOutputs.length),
      timestamp: it.timestamp,
    }))
    setIterations(mapped)
  }

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">Iteration Inspector</h1>
        <p className="text-sm text-muted-foreground">Inspect iteration traces for a given job.</p>
      </header>

      <Card className="ra9-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Load Trace</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex flex-col items-start gap-3 md:flex-row md:items-center">
            <input
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm md:w-80"
              style={{ borderColor: "var(--ra9-border)" }}
              placeholder="Enter job id (e.g., job_abcd)"
              aria-label="Job ID"
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
            />
            <button
              className="rounded-md bg-[color:var(--ra9-primary)] px-3 py-2 text-sm text-[color:var(--ra9-bg-0)] hover:opacity-90"
              onClick={loadTrace}
              aria-label="Load trace"
            >
              Load
            </button>
          </div>
        </CardContent>
      </Card>

      {!!iterations.length && (
        <section className="mt-6">
          <IterationTimeline iterations={iterations} />
        </section>
      )}
    </main>
  )
}
