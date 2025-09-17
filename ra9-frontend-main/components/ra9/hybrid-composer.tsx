"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { cn } from "@/lib/utils"

export type JobId = string

export type QueryRequest = {
  sessionId: string
  userId: string
  text: string
  mode: "concise" | "deep" | "debate" | "planner"
  loopDepth: number
  allowMemoryWrite: boolean
}

export type HybridComposerProps = {
  userId: string
  initialMode?: QueryRequest["mode"]
  defaultLoopDepth?: number // 1..6
  onSubmit: (req: QueryRequest) => Promise<JobId>
}

const MODES: QueryRequest["mode"][] = ["concise", "deep", "debate", "planner"]

export default function HybridComposer(props: HybridComposerProps) {
  const { userId, initialMode = "concise", defaultLoopDepth = 2, onSubmit } = props

  const [text, setText] = useState<string>("")
  const [mode, setMode] = useState<QueryRequest["mode"]>(initialMode)
  const [loopDepth, setLoopDepth] = useState<number>(defaultLoopDepth)
  const [allowMemoryWrite, setAllowMemoryWrite] = useState<boolean>(false)
  const [showMemoryModal, setShowMemoryModal] = useState<boolean>(false)
  const [submitting, setSubmitting] = useState<boolean>(false)

  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const tokenEstimate = useMemo(() => Math.max(10, Math.ceil(text.length / 4)), [text])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault()
        textareaRef.current?.focus()
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault()
        handleSend()
      }
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [text, mode, loopDepth, allowMemoryWrite])

  const handleMemoryToggle = () => {
    if (!allowMemoryWrite) {
      // opening: confirm consent
      setShowMemoryModal(true)
    } else {
      // turning off
      setAllowMemoryWrite(false)
    }
  }

  const confirmMemory = (choice: "ephemeral" | "session" | "permanent" | "cancel") => {
    if (choice === "cancel") {
      setShowMemoryModal(false)
      return
    }
    setAllowMemoryWrite(true)
    setShowMemoryModal(false)
  }

  const handleSend = async () => {
    if (!text.trim() || submitting) return
    setSubmitting(true)
    try {
      const jobId = await onSubmit({
        sessionId: "", // will be filled by page wrapper before calling
        userId,
        text: text.trim(),
        mode,
        loopDepth,
        allowMemoryWrite,
      } as any) // page ensures sessionId
      // Clear after submit
      setText("")
      // Optionally, we could surface jobId here
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="bg-background/60 rounded-xl p-4 border border-border shadow-sm backdrop-blur-md">
      {/* Mode pills */}
      <div className="flex flex-wrap gap-2 mb-3" role="tablist" aria-label="Composer mode">
        {MODES.map((m) => (
          <button
            key={m}
            role="tab"
            aria-selected={mode === m}
            onClick={() => setMode(m)}
            className={cn(
              "px-3 py-1.5 rounded-full text-sm border",
              mode === m
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-card text-foreground border-border",
            )}
          >
            {m}
          </button>
        ))}
        <div className="ml-auto flex items-center gap-3">
          <MemoryToggle onClick={handleMemoryToggle} active={allowMemoryWrite} />
          <LoopDial value={loopDepth} onChange={setLoopDepth} />
          <div className="text-xs text-muted-foreground">
            est. tokens {tokenEstimate} • depth {loopDepth}
          </div>
        </div>
      </div>

      <textarea
        ref={textareaRef}
        className="w-full bg-transparent resize-none outline-none text-base leading-relaxed placeholder:text-muted-foreground"
        rows={3}
        placeholder="Ask RA9 anything… Ctrl+K to focus, Ctrl+Enter to send"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="flex items-center justify-between mt-3">
        <div className="text-xs text-muted-foreground">
          Mode: {mode} • Memory: {allowMemoryWrite ? "on" : "off"}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSend}
            disabled={submitting || !text.trim()}
            className={cn(
              "rounded-lg px-4 py-2 text-sm font-medium",
              submitting || !text.trim()
                ? "bg-muted text-muted-foreground cursor-not-allowed"
                : "bg-primary text-primary-foreground",
            )}
          >
            {submitting ? "Running…" : "Run"}
          </button>
        </div>
      </div>

      {showMemoryModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Save to Memory?"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        >
          <div className="bg-background border border-border rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold">Save to Memory?</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Choose how RA9 should store this session. You can change this later in Settings.
            </p>
            <div className="flex gap-2 mt-4">
              <button
                className="px-3 py-2 rounded bg-primary text-primary-foreground"
                onClick={() => confirmMemory("ephemeral")}
              >
                Ephemeral
              </button>
              <button className="px-3 py-2 rounded border border-border" onClick={() => confirmMemory("session")}>
                Session
              </button>
              <button className="px-3 py-2 rounded border border-border" onClick={() => confirmMemory("permanent")}>
                Permanent
              </button>
              <button className="px-3 py-2 rounded text-muted-foreground" onClick={() => confirmMemory("cancel")}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function MemoryToggle({ active, onClick }: { active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "text-xs px-2 py-1 rounded border",
        active ? "bg-primary text-primary-foreground border-primary" : "bg-card border-border",
      )}
      aria-pressed={active}
      aria-label="Toggle memory write"
      title="If enabled, RA9 may write outputs to memory (with consent)."
    >
      Memory {active ? "ON" : "OFF"}
    </button>
  )
}

function LoopDial({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  // Simple range dial; replace with circular control later
  return (
    <div className="flex items-center gap-2">
      <label className="text-xs text-muted-foreground">Depth</label>
      <input
        type="range"
        min={1}
        max={6}
        value={value}
        onChange={(e) => onChange(Number.parseInt(e.target.value, 10))}
        aria-label="Deliberation depth"
      />
      <span className="text-xs">{value}</span>
    </div>
  )
}
