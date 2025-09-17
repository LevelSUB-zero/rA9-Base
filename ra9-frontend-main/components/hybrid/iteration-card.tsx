"use client"

import type { Iteration } from "@/types/hybrid"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function IterationCard({ it }: { it: Iteration }) {
  return (
    <div className="border rounded-lg p-3 bg-background/60 backdrop-blur">
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium">
          Iteration {it.iterationIndex} • {new Date(it.timestamp).toLocaleTimeString()}
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span
            className="font-medium"
            style={{ color: it.verifier.passed ? ("var(--ra9-primary)" as any) : ("var(--ra9-accent)" as any) }}
          >
            {it.verifier.passed ? "Verified" : "Unverified"}
          </span>
          <div className="w-16 h-2 bg-foreground/10 rounded-full" aria-label="confidence">
            <div
              className="h-2 rounded-full"
              style={{
                width: `${Math.round((it.verifier.score ?? 0) * 100)}%`,
                background: "var(--ra9-primary)",
              }}
            />
          </div>
        </div>
      </div>

      <div className="mt-2 text-sm opacity-80" aria-describedby={`iter-${it.iterationIndex}-delta`}>
        {it.deltaSummary}
      </div>

      <Tabs className="mt-3" defaultValue={it.agentOutputs[0]?.agentName ?? "logical"}>
        <TabsList>
          {it.agentOutputs.map((a) => (
            <TabsTrigger key={a.agentName} value={a.agentName}>
              {a.agentName}
            </TabsTrigger>
          ))}
        </TabsList>
        {it.agentOutputs.map((a) => (
          <TabsContent key={a.agentName} value={a.agentName}>
            <div className="text-sm whitespace-pre-wrap">{a.text}</div>
          </TabsContent>
        ))}
      </Tabs>

      <div className="mt-3 text-xs">
        <div className="font-medium">Memory hits</div>
        <div className="flex flex-wrap gap-2 mt-1">
          {it.memoryHits.map((m) => (
            <span key={m.id} className="px-2 py-1 rounded bg-foreground/10">
              {m.id} ({Math.round(m.score * 100)}%)
            </span>
          ))}
        </div>
      </div>

      <div className="mt-2 text-xs">
        <div className="font-medium">Citations</div>
        <ul className="list-disc list-inside">
          {it.citations.map((c, i) => (
            <li key={i}>
              <a
                className="underline underline-offset-2"
                style={{ textDecorationColor: "var(--ra9-primary)" as any }}
                href={c.url}
                target="_blank"
                rel="noreferrer"
              >
                {c.source}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
