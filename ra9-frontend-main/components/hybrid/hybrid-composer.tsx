"use client"
import { useState, useRef, useEffect } from "react"
import type { HybridComposerProps, QueryRequest, JobId } from "@/types/hybrid"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Slider } from "@/components/ui/slider"

export function HybridComposer(props: HybridComposerProps) {
  const { userId, initialMode = "concise", defaultLoopDepth = 2, onSubmit } = props

  const [mode, setMode] = useState<HybridComposerProps["initialMode"]>(initialMode)
  const [text, setText] = useState("")
  const [allowMemoryWrite, setAllowMemoryWrite] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [loopDepth, setLoopDepth] = useState(defaultLoopDepth)
  const [submitting, setSubmitting] = useState(false)
  const [costEstimate, setCostEstimate] = useState<number>(0)
  const [latencyMs, setLatencyMs] = useState<number>(0)

  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  // Keyboard: Ctrl+K focus, Ctrl+Enter submit
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key.toLowerCase() === "k") {
        e.preventDefault()
        textareaRef.current?.focus()
      } else if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault()
        doSubmit()
      }
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [text, mode, loopDepth, allowMemoryWrite])

  // naive token estimate: words * depth
  useEffect(() => {
    const words = text.trim().split(/\s+/).filter(Boolean).length
    setCostEstimate(Math.round(words * Math.max(1, loopDepth) * 0.002 * 1000) / 1000)
  }, [text, loopDepth])

  async function doSubmit() {
    if (!text.trim() || submitting) return
    if (allowMemoryWrite && !confirmOpen) {
      // Ask consent before first write
      setConfirmOpen(true)
      return
    }
    setSubmitting(true)
    const start = performance.now()
    try {
      const req: QueryRequest = {
        sessionId: "session_1",
        userId,
        text,
        mode,
        loopDepth,
        allowMemoryWrite,
      }
      const jobId: JobId = await onSubmit(req)
      const end = performance.now()
      setLatencyMs(Math.max(0, Math.round(end - start)))
      setText("")
    } catch (e) {
      console.error("[v0] composer submit error", e)
    } finally {
      setSubmitting(false)
    }
  }

  function confirmMemory(choice: "ephemeral" | "session" | "permanent") {
    // For now, any choice enables writes; store chosen policy elsewhere if needed
    setAllowMemoryWrite(true)
    setConfirmOpen(false)
  }

  return (
    <div className="bg-background/60 backdrop-blur-md border rounded-xl p-4 shadow-md">
      {/* mode pills */}
      <div className="flex gap-2 mb-3" role="tablist" aria-label="Composer mode">
        {(["concise", "deep", "debate", "planner"] as const).map((m) => {
          const active = m === mode
          return (
            <button
              key={m}
              role="tab"
              aria-selected={active}
              onClick={() => setMode(m)}
              className={`px-3 py-1 rounded-md text-sm border ${
                active
                  ? "bg-[color:var(--ra9-primary)] text-[color:var(--ra9-bg-0)] border-[color:var(--ra9-primary)]"
                  : "bg-transparent text-foreground/80 hover:bg-foreground/5"
              }`}
            >
              {m}
            </button>
          )
        })}
      </div>

      {/* textarea */}
      <textarea
        ref={textareaRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask RA9 anything…"
        className="w-full bg-transparent resize-none outline-none text-base min-h-24"
        aria-label="Chat input"
      />

      <div className="flex items-center justify-between mt-3 gap-3">
        <div className="flex items-center gap-4">
          {/* Depth dial (slider 1..6) */}
          <div className="flex items-center gap-2">
            <Label htmlFor="depth" className="text-sm">
              Depth
            </Label>
            <div className="w-28">
              <Slider
                id="depth"
                min={1}
                max={6}
                step={1}
                value={[loopDepth]}
                onValueChange={(v) => setLoopDepth(v[0] as number)}
              />
            </div>
            <span className="text-sm tabular-nums">{loopDepth}</span>
          </div>

          {/* Memory write toggle (consent modal when enabling) */}
          <div className="flex items-center gap-2">
            <Switch
              id="mem"
              checked={allowMemoryWrite}
              onCheckedChange={(checked) => {
                if (checked) setConfirmOpen(true)
                else setAllowMemoryWrite(false)
              }}
            />
            <Label htmlFor="mem" className="text-sm">
              Memory write
            </Label>
          </div>

          {/* Cost & latency */}
          <div className="text-xs text-foreground/70">
            est. cost ~ {costEstimate} | last latency {latencyMs}ms
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            disabled={submitting || !text.trim()}
            onClick={doSubmit}
            className="bg-[color:var(--ra9-primary)] text-[color:var(--ra9-bg-0)] hover:opacity-90"
          >
            {submitting ? "Running…" : "Run"}
          </Button>
        </div>
      </div>

      {/* Memory consent modal */}
      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Save to Memory?</DialogTitle>
            <DialogDescription>
              Choose how RA9 should store this session’s data. You can change this later in Settings.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-2 mt-2">
            <Button onClick={() => confirmMemory("ephemeral")} variant="secondary">
              Ephemeral (1 hour)
            </Button>
            <Button onClick={() => confirmMemory("session")} variant="secondary">
              Session
            </Button>
            <Button
              onClick={() => confirmMemory("permanent")}
              className="bg-[color:var(--ra9-accent)] text-[color:var(--ra9-bg-0)] hover:opacity-90"
            >
              Permanent (review)
            </Button>
          </div>
          <DialogFooter>
            <Button
              variant="ghost"
              onClick={() => {
                setAllowMemoryWrite(false)
                setConfirmOpen(false)
              }}
            >
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
