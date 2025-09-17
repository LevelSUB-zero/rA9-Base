"use client"
import { cn } from "@/lib/utils"

type DialProps = {
  value: number // 1..6
  onChange: (v: number) => void
  className?: string
}

export function DeliberationDial({ value, onChange, className }: DialProps) {
  const inc = () => onChange(Math.min(6, value + 1))
  const dec = () => onChange(Math.max(1, value - 1))

  return (
    <div
      role="slider"
      aria-label="Deliberation depth"
      aria-valuemin={1}
      aria-valuemax={6}
      aria-valuenow={value}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "ArrowRight" || e.key === "ArrowUp") {
          inc()
          e.preventDefault()
        }
        if (e.key === "ArrowLeft" || e.key === "ArrowDown") {
          dec()
          e.preventDefault()
        }
      }}
      className={cn(
        "relative flex h-20 w-20 select-none items-center justify-center rounded-full border",
        "border-[color:var(--ra9-border)] bg-[color:var(--ra9-surface-1)]",
        "transition-transform duration-200",
        className,
      )}
      onClick={inc}
      title="Adjust deliberation depth"
    >
      <span className="sr-only">Current depth</span>
      <svg
        viewBox="0 0 100 100"
        className="h-14 w-14"
        style={{
          transition: "transform 200ms var(--ra9-ease-standard)",
          transform: `rotate(${(value - 1) * 36}deg)`,
        }}
      >
        <circle cx="50" cy="50" r="44" fill="none" stroke="var(--ra9-border)" strokeWidth="4" />
        <path d="M50 8 L54 18 L46 18 Z" fill="var(--ra9-primary)" className="drop-shadow-sm" />
      </svg>
      <div
        className="pointer-events-none absolute -bottom-2 rounded-full px-2 py-0.5 text-xs"
        style={{
          background: "color-mix(in srgb, var(--ra9-primary) 25%, transparent)",
          border: "1px solid var(--ra9-border)",
        }}
      >
        {value}
      </div>
    </div>
  )
}
