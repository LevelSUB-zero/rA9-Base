"use client"

import * as React from "react"
import { useState, useEffect } from "react"
import type { IterationTimelineProps } from "@/types/hybrid"
import { IterationCard } from "./iteration-card"

export function IterationTimeline({ iterations, onSelect }: IterationTimelineProps) {
  const [openIndex, setOpenIndex] = React.useState<number | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  function toggle(i: number) {
    const next = openIndex === i ? null : i
    setOpenIndex(next)
    onSelect(i)
  }

  return (
    <div className="space-y-3">
      {iterations.map((it) => (
        <div key={it.iterationIndex}>
          <button
            className="w-full flex items-center justify-between text-left px-2 py-2 rounded-md hover:bg-foreground/5 border"
            onClick={() => toggle(it.iterationIndex)}
            aria-expanded={openIndex === it.iterationIndex}
          >
            <div className="text-sm font-medium flex items-center gap-2">
              <span
                className="inline-block w-2 h-2 rounded-full"
                style={{
                  background: it.verifier.passed ? ("var(--ra9-primary)" as any) : ("var(--ra9-accent)" as any),
                }}
              />
              Iteration {it.iterationIndex}
            </div>
            <div className="text-xs opacity-70">
              {mounted ? new Date(it.timestamp).toLocaleTimeString() : new Date(it.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
            </div>
          </button>
          {openIndex === it.iterationIndex ? (
            <div className="mt-2">
              <IterationCard it={it} />
            </div>
          ) : null}
        </div>
      ))}
    </div>
  )
}
