"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export type PlannerNode = {
  id: string
  title: string
  confidence?: number
}

export type PlannerConnection = { from: string; to: string }

export type PlannerCanvasProps = {
  nodes: PlannerNode[]
  connections: PlannerConnection[]
  onAddNode?: (title: string) => void
  onConnect?: (from: string, to: string) => void
  className?: string
}

export function PlannerCanvas({ nodes, connections, onAddNode, onConnect, className }: PlannerCanvasProps) {
  const [title, setTitle] = React.useState("New step")
  const [from, setFrom] = React.useState<string>("")
  const [to, setTo] = React.useState<string>("")

  return (
    <section className={cn("ra9-card p-4", className)} aria-label="Planner canvas">
      <header className="mb-3 flex items-center justify-between">
        <div className="text-sm">Planner</div>
      </header>

      <div className="mb-3 grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="rounded-lg border p-3" style={{ borderColor: "var(--ra9-border)" }}>
          <div className="mb-2 text-xs text-muted-foreground">Add node</div>
          <input
            className="w-full rounded-md border bg-transparent px-2 py-1 text-sm"
            style={{ borderColor: "var(--ra9-border)" }}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            aria-label="New node title"
          />
          <Button
            className="mt-2 w-full bg-[color:var(--ra9-primary)] text-[color:var(--ra9-bg-0)] hover:opacity-90"
            onClick={() => onAddNode?.(title)}
          >
            Add
          </Button>
        </div>
        <div className="rounded-lg border p-3" style={{ borderColor: "var(--ra9-border)" }}>
          <div className="mb-2 text-xs text-muted-foreground">Connect nodes</div>
          <select
            aria-label="From node"
            className="mb-2 w-full rounded-md border bg-transparent px-2 py-1 text-sm"
            style={{ borderColor: "var(--ra9-border)" }}
            value={from}
            onChange={(e) => setFrom(e.target.value)}
          >
            <option value="">From…</option>
            {nodes.map((n) => (
              <option key={n.id} value={n.id}>
                {n.title}
              </option>
            ))}
          </select>
          <select
            aria-label="To node"
            className="mb-2 w-full rounded-md border bg-transparent px-2 py-1 text-sm"
            style={{ borderColor: "var(--ra9-border)" }}
            value={to}
            onChange={(e) => setTo(e.target.value)}
          >
            <option value="">To…</option>
            {nodes.map((n) => (
              <option key={n.id} value={n.id}>
                {n.title}
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            className="w-full border-border bg-transparent"
            onClick={() => from && to && onConnect?.(from, to)}
          >
            Connect
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {nodes.map((n) => (
          <div
            key={n.id}
            className="rounded-lg border p-3"
            style={{
              borderColor: "var(--ra9-border)",
              background: "var(--ra9-surface-1)",
              backdropFilter: "blur(8px)",
            }}
          >
            <div className="text-sm font-medium">{n.title}</div>
            {typeof n.confidence === "number" && (
              <div className="mt-2 text-xs text-muted-foreground">Confidence: {Math.round(n.confidence * 100)}%</div>
            )}
          </div>
        ))}
      </div>

      {!!connections.length && (
        <div className="mt-3 rounded-lg border p-3 text-sm" style={{ borderColor: "var(--ra9-border)" }}>
          <div className="mb-1 text-xs uppercase tracking-wide text-muted-foreground">Connections</div>
          <ul className="list-disc space-y-1 pl-5">
            {connections.map((c, i) => (
              <li key={`${c.from}-${c.to}-${i}`}>
                {c.from} → {c.to}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
