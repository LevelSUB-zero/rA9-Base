"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"

export type ToolRunInputs = Record<string, unknown>

export type ToolRunnerProps = {
  toolId: string
  inputs: ToolRunInputs
  dryRun: boolean
  onPreflight?: (toolId: string, inputs: ToolRunInputs) => Promise<string[]>
  onRun?: (toolId: string, inputs: ToolRunInputs, dryRun: boolean) => Promise<{ ok: boolean; output: string }>
  className?: string
}

export function ToolRunner({ toolId, inputs, dryRun, onPreflight, onRun, className }: ToolRunnerProps) {
  const [localDry, setLocalDry] = React.useState(dryRun)
  const [preflight, setPreflight] = React.useState<string[] | null>(null)
  const [output, setOutput] = React.useState<string>("")
  const [busy, setBusy] = React.useState(false)

  async function handlePreflight() {
    setBusy(true)
    try {
      const checks = await (onPreflight?.(toolId, inputs) ??
        Promise.resolve(["Sandbox available", "No external network calls in dry-run", "Input schema valid"]))
      setPreflight(checks)
    } finally {
      setBusy(false)
    }
  }

  async function handleRun() {
    setBusy(true)
    try {
      const result = await (onRun?.(toolId, inputs, localDry) ??
        Promise.resolve({ ok: true, output: `Dry-run of ${toolId} succeeded.` }))
      setOutput(result.output)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className={cn("ra9-card p-4", className)} aria-label={`Tool runner for ${toolId}`}>
      <header className="mb-3 flex items-center justify-between gap-2">
        <div className="text-sm">
          <strong>Tool:</strong> {toolId}
        </div>
        <div className="flex items-center gap-2">
          <Switch id="dryrun" checked={localDry} onCheckedChange={setLocalDry} />
          <Label htmlFor="dryrun" className="text-xs text-muted-foreground">
            Dry-run
          </Label>
        </div>
      </header>

      <div className="mb-3">
        <Label className="text-xs text-muted-foreground">Inputs (JSON)</Label>
        <Textarea
          aria-label="Tool inputs"
          className="mt-1 min-h-24 bg-transparent"
          readOnly
          value={JSON.stringify(inputs, null, 2)}
        />
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          className="border-border bg-transparent"
          disabled={busy}
          onClick={handlePreflight}
          aria-label="Run preflight checks"
        >
          Preflight
        </Button>
        <Button
          className="bg-[color:var(--ra9-primary)] text-[color:var(--ra9-bg-0)] hover:opacity-90"
          disabled={busy}
          onClick={handleRun}
          aria-label="Execute tool"
        >
          {localDry ? "Run Dry-Run" : "Execute"}
        </Button>
      </div>

      {preflight && (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-muted-foreground" aria-label="Preflight results">
          {preflight.map((p, i) => (
            <li key={i}>{p}</li>
          ))}
        </ul>
      )}

      {!!output && (
        <div className="mt-3 rounded-lg border p-3" style={{ borderColor: "var(--ra9-border)" }}>
          <div className="mb-1 text-xs uppercase tracking-wide text-muted-foreground">Sandbox Output</div>
          <pre className="whitespace-pre-wrap text-sm">{output}</pre>
        </div>
      )}
    </section>
  )
}
