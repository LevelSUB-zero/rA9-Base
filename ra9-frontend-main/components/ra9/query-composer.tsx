"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { DeliberationDial } from "./deliberation-dial"

export type JobId = string

export type QueryRequest = {
  userId: string
  text: string
  mode: "concise" | "deep" | "debate" | "planner"
  allowMemoryWrite: boolean
  loopDepth: number
}

export type QueryComposerProps = {
  userId: string
  initialText?: string
  mode: "concise" | "deep" | "debate" | "planner"
  allowMemoryWrite: boolean
  loopDepth: number // 1..6
  onSubmit: (q: QueryRequest) => Promise<JobId>
  className?: string
}

const modes: Array<QueryRequest["mode"]> = ["concise", "deep", "debate", "planner"]

export function QueryComposer(props: QueryComposerProps) {
  const [text, setText] = React.useState(props.initialText ?? "")
  const [mode, setMode] = React.useState<QueryRequest["mode"]>(props.mode)
  const [allowMemory, setAllowMemory] = React.useState(props.allowMemoryWrite)
  const [depth, setDepth] = React.useState(props.loopDepth)
  const [submitting, setSubmitting] = React.useState(false)

  async function handleSubmit() {
    if (!text.trim()) return
    setSubmitting(true)
    try {
      const jobId = await props.onSubmit({
        userId: props.userId,
        text,
        mode,
        allowMemoryWrite: allowMemory,
        loopDepth: depth,
      })
      console.log("[v0] Job queued:", jobId)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-3", props.className)}>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-muted-foreground">Mode</span>
        <div className="flex rounded-lg border border-[color:var(--ra9-border)] p-1">
          {modes.map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={cn(
                "px-2.5 py-1 text-xs rounded-md transition-colors",
                m === mode
                  ? "bg-[color:var(--ra9-primary)] text-[color:var(--ra9-bg-0)]"
                  : "text-muted-foreground hover:bg-[color:var(--ra9-surface-1)]",
              )}
              aria-pressed={m === mode}
            >
              {m}
            </button>
          ))}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Switch id="memory" checked={allowMemory} onCheckedChange={setAllowMemory} />
          <Label htmlFor="memory" className="text-xs text-muted-foreground">
            Memory write
          </Label>
        </div>
      </div>

      <Textarea
        placeholder="Ask RA9 anything…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="min-h-28 resize-y bg-transparent focus-visible:ring-[color:var(--ra9-primary)]"
        aria-label="Query input"
      />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 rounded-xl border border-[color:var(--ra9-border)] px-3 py-2">
          <span className="text-xs text-muted-foreground">Cost</span>
          <span className="text-xs">~$0.00</span>
          <div className="h-4 w-px bg-[color:var(--ra9-border)]" />
          <span className="text-xs text-muted-foreground">Latency</span>
          <span className="text-xs">—</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Depth</span>
            <DeliberationDial value={depth} onChange={setDepth} />
          </div>
          <Button
            onClick={handleSubmit}
            disabled={submitting || !text.trim()}
            className="bg-[color:var(--ra9-primary)] text-[color:var(--ra9-bg-0)] hover:opacity-90"
          >
            {submitting ? "Submitting…" : "Run"}
          </Button>
        </div>
      </div>
    </div>
  )
}
