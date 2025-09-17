"use client"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export type MemoryType = "episodic" | "semantic" | "procedural"

export type MemoryCardProps = {
  id: string
  type: MemoryType
  text: string
  embedVector?: number[]
  timestamp: string
  tags?: string[]
  redactFlag?: boolean
  onApprove?: (id: string) => void
  onRedact?: (id: string) => void
  onEdit?: (id: string) => void
  onExport?: (id: string) => void
  className?: string
}

export function MemoryCard({
  id,
  type,
  text,
  timestamp,
  tags = [],
  redactFlag = false,
  onApprove,
  onRedact,
  onEdit,
  onExport,
  className,
}: MemoryCardProps) {
  return (
    <article
      className={cn("ra9-card p-4 outline-none", redactFlag ? "opacity-75" : "", className)}
      aria-label={`Memory ${id}`}
    >
      <header className="mb-2 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            aria-hidden
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ background: "var(--ra9-primary)" }}
          />
          <span className="text-xs uppercase tracking-wide text-muted-foreground">{type}</span>
        </div>
        <time className="text-xs text-muted-foreground" dateTime={timestamp}>
          {new Date(timestamp).toLocaleString()}
        </time>
      </header>

      <p className="text-sm leading-relaxed">{text}</p>

      {!!tags.length && (
        <div className="mt-3 flex flex-wrap gap-2">
          {tags.map((t) => (
            <span key={t} className="ra9-chip px-2 py-0.5 text-xs text-muted-foreground">
              {t}
            </span>
          ))}
        </div>
      )}

      <footer className="mt-4 flex flex-wrap items-center gap-2">
        <Button
          size="sm"
          variant="outline"
          className="border-border text-foreground bg-transparent"
          onClick={() => onApprove?.(id)}
          aria-label="Approve memory"
        >
          Approve
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="border-border text-[color:var(--ra9-accent)] bg-transparent"
          onClick={() => onRedact?.(id)}
          aria-label="Redact memory"
        >
          Redact
        </Button>
        <Button size="sm" variant="ghost" onClick={() => onEdit?.(id)} aria-label="Edit memory">
          Edit
        </Button>
        <Button size="sm" variant="ghost" onClick={() => onExport?.(id)} aria-label="Export memory">
          Export
        </Button>
        {redactFlag && (
          <Badge className="ml-auto bg-[color:var(--ra9-accent)] text-[color:var(--ra9-bg-0)]">Pending Redaction</Badge>
        )}
      </footer>
    </article>
  )
}
