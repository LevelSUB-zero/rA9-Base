"use client"

export type StreamToken = { text: string; kind: "verified" | "speculative" }
export type CompactTokenStreamerProps = {
  tokens: StreamToken[]
  className?: string
}

export function CompactTokenStreamer({ tokens, className }: CompactTokenStreamerProps) {
  return (
    <div className={className} aria-live="polite" aria-atomic="false">
      {tokens.map((t, i) => (
        <span
          key={i}
          className="whitespace-pre-wrap"
          style={{
            textDecoration: "underline",
            textDecorationColor: t.kind === "verified" ? "var(--ra9-primary)" : "var(--ra9-accent)",
            textDecorationThickness: "1px",
          }}
        >
          {t.text}
        </span>
      ))}
    </div>
  )
}
