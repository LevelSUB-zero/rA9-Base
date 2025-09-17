"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { QueryComposer } from "@/components/ra9/query-composer"
import { IterationTimeline } from "@/components/ra9/iteration-timeline"
import { MemoryCard } from "@/components/ra9/memory-card"
import { ToolRunner } from "@/components/ra9/tool-runner"
import { PlannerCanvas } from "@/components/ra9/planner-canvas"
import { StreamView } from "@/components/ra9/stream-view"
import { useUIPrefs } from "@/components/ra9/ui-prefs"
import * as React from "react"

export default function Page() {
  const { memoryConsentDefault } = useUIPrefs()
  const [jobId, setJobId] = React.useState<string | null>(null)

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-8">
      <header className="mb-6 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-balance text-3xl font-semibold tracking-tight">RA9 Workspace</h1>
          <p className="text-sm text-muted-foreground">
            Compose queries, inspect iterations, and control deliberation depth.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="border-border text-foreground bg-transparent">
            Settings
          </Button>
          <Button className="bg-[color:var(--ra9-primary)] text-[color:var(--ra9-bg-0)] hover:opacity-90">
            New Session
          </Button>
        </div>
      </header>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card className="ra9-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Quick Composer</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <QueryComposer
              userId="demo_user"
              mode="deep"
              allowMemoryWrite={memoryConsentDefault}
              loopDepth={2}
              onSubmit={async (q) => {
                const res = await fetch("/api/v1/query", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    text: q.text,
                    mode: q.mode,
                    memoryWrite: q.allowMemoryWrite,
                    userId: q.userId,
                    meta: { loopDepth: q.loopDepth },
                  }),
                })
                const data = await res.json()
                setJobId(data.jobId)
                return data.jobId as string
              }}
            />
          </CardContent>
        </Card>

        <Card className="ra9-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Iteration Timeline</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <IterationTimeline
              iterations={[
                {
                  id: "it-0",
                  index: 0,
                  summary: "Initial reasoning draft with citations pending.",
                  confidence: 0.72,
                  timestamp: new Date().toISOString(),
                },
                {
                  id: "it-1",
                  index: 1,
                  summary: "Refined answer, added two citations and removed speculation.",
                  confidence: 0.84,
                  timestamp: new Date().toISOString(),
                },
              ]}
            />
          </CardContent>
        </Card>
      </section>

      <section className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <MemoryCard
          id="m-1"
          type="semantic"
          text="Summary of user’s preferred tone: concise, formal; avoid speculation without citations."
          timestamp={new Date().toISOString()}
          tags={["profile", "tone", "policy"]}
          onApprove={(id) => console.log("[v0] approve", id)}
          onRedact={(id) => console.log("[v0] redact", id)}
          onEdit={(id) => console.log("[v0] edit", id)}
          onExport={(id) => console.log("[v0] export", id)}
        />
        <ToolRunner toolId="xman.web.fetch" inputs={{ url: "https://example.com", method: "GET" }} dryRun={true} />
      </section>

      <section className="mt-6">
        <PlannerCanvas
          nodes={[
            { id: "n1", title: "Gather Sources", confidence: 0.8 },
            { id: "n2", title: "Draft Answer", confidence: 0.7 },
            { id: "n3", title: "Verify Citations", confidence: 0.9 },
          ]}
          connections={[
            { from: "n1", to: "n2" },
            { from: "n2", to: "n3" },
          ]}
          onAddNode={(title) => console.log("[v0] add node", title)}
          onConnect={(from, to) => console.log("[v0] connect", from, to)}
        />
      </section>

      {jobId && (
        <section className="mt-6">
          <StreamView jobId={jobId} />
        </section>
      )}
    </main>
  )
}
