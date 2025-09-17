"use client"

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { QueryComposer } from "@/components/ra9/query-composer"
import { StreamView } from "@/components/ra9/stream-view"
import { useUIPrefs } from "@/components/ra9/ui-prefs"

export default function ComposerPage() {
  const [jobId, setJobId] = React.useState<string | null>(null)
  const { memoryConsentDefault } = useUIPrefs()

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">Composer</h1>
        <p className="text-sm text-muted-foreground">Full workspace for composing queries with live streaming.</p>
      </header>

      <Card className="ra9-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Query</CardTitle>
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

      {jobId && (
        <section className="mt-6">
          <StreamView jobId={jobId} />
        </section>
      )}
    </main>
  )
}
