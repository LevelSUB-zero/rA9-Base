"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { QueryComposer } from "@/components/ra9/query-composer"

export default function DashboardPage() {
  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Snapshot of sessions, goals, health, and a quick composer.</p>
      </header>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card className="ra9-card md:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Quick Composer</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <QueryComposer
              userId="demo_user"
              mode="concise"
              allowMemoryWrite={false}
              loopDepth={2}
              onSubmit={async () => "job_mock_dashboard"}
            />
          </CardContent>
        </Card>

        <Card className="ra9-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">System Health</CardTitle>
          </CardHeader>
          <CardContent className="pt-0 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Throughput</span>
              <span>OK</span>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-muted-foreground">Avg Iterations</span>
              <span>2.1</span>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-muted-foreground">Verification Fail</span>
              <span>0.9%</span>
            </div>
          </CardContent>
        </Card>

        <Card className="ra9-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Recent Sessions</CardTitle>
          </CardHeader>
          <CardContent className="pt-0 text-sm">
            <ul className="space-y-2">
              <li className="flex items-center justify-between">
                <span>Session A</span>
                <span className="text-muted-foreground">2 iterations</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Session B</span>
                <span className="text-muted-foreground">3 iterations</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Session C</span>
                <span className="text-muted-foreground">1 iteration</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="ra9-card md:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Active Goals</CardTitle>
          </CardHeader>
          <CardContent className="pt-0 text-sm">
            <ul className="grid grid-cols-1 gap-2 md:grid-cols-2">
              <li className="rounded-lg border p-3" style={{ borderColor: "var(--ra9-border)" }}>
                Improve citation coverage to 90%
              </li>
              <li className="rounded-lg border p-3" style={{ borderColor: "var(--ra9-border)" }}>
                Reduce token latency p50 below 200ms
              </li>
            </ul>
          </CardContent>
        </Card>
      </section>
    </main>
  )
}
