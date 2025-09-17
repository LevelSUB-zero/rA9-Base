"use client"
import { cn } from "@/lib/utils"

export type CitationBadgeProps = {
  source: string
  confidence: number // 0..1
  href?: string
  className?: string
}

export function CitationBadge({ source, confidence, href, className }: CitationBadgeProps) {
  const color = confidence >= 0.75 ? "var(--ra9-primary)" : "var(--ra9-accent)"
  const content = (
    <span
      className={cn("inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs", className)}
      style={{ border: `1px solid ${color}`, color }}
      aria-label={`Citation ${source} confidence ${Math.round(confidence * 100)}%`}
    >
      <span aria-hidden>◆</span>
      <span>{source}</span>
      <span className="text-[0.7em] opacity-75">{Math.round(confidence * 100)}%</span>
    </span>
  )
  return href ? (
    <a href={href} target="_blank" rel="noreferrer noopener" className="hover:opacity-90">
      {content}
    </a>
  ) : (
    content
  )
}
