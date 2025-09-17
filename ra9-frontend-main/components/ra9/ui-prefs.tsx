"use client"

import * as React from "react"

export type UIPrefs = {
  reducedMotion: boolean
  highContrast: boolean
  memoryConsentDefault: boolean
  setReducedMotion: (v: boolean) => void
  setHighContrast: (v: boolean) => void
  setMemoryConsentDefault: (v: boolean) => void
}

const Ctx = React.createContext<UIPrefs | null>(null)

function readBool(key: string, fallback = false) {
  if (typeof window === "undefined") return fallback
  const v = window.localStorage.getItem(key)
  return v === "1" ? true : v === "0" ? false : fallback
}

function writeBool(key: string, v: boolean) {
  if (typeof window === "undefined") return
  window.localStorage.setItem(key, v ? "1" : "0")
}

export function UIPrefsProvider({ children }: { children: React.ReactNode }) {
  const [reducedMotion, setReducedMotionState] = React.useState(false)
  const [highContrast, setHighContrastState] = React.useState(false)
  const [memoryConsentDefault, setMemoryConsentDefaultState] = React.useState(false)

  // Initialize from localStorage and media queries
  React.useEffect(() => {
    const prefersReduced =
      typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
    setReducedMotionState(readBool("ui.rm", prefersReduced))
    setHighContrastState(readBool("ui.hc", false))
    setMemoryConsentDefaultState(readBool("ui.mem", false))
  }, [])

  // Reflect into DOM classList for CSS hooks
  React.useEffect(() => {
    if (typeof document === "undefined") return
    document.body.classList.toggle("rm", reducedMotion)
  }, [reducedMotion])

  React.useEffect(() => {
    if (typeof document === "undefined") return
    document.body.classList.toggle("hc", highContrast)
  }, [highContrast])

  const setReducedMotion = (v: boolean) => {
    setReducedMotionState(v)
    writeBool("ui.rm", v)
  }
  const setHighContrast = (v: boolean) => {
    setHighContrastState(v)
    writeBool("ui.hc", v)
  }
  const setMemoryConsentDefault = (v: boolean) => {
    setMemoryConsentDefaultState(v)
    writeBool("ui.mem", v)
  }

  const value: UIPrefs = {
    reducedMotion,
    highContrast,
    memoryConsentDefault,
    setReducedMotion,
    setHighContrast,
    setMemoryConsentDefault,
  }

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useUIPrefs() {
  const ctx = React.useContext(Ctx)
  if (!ctx) throw new Error("useUIPrefs must be used within UIPrefsProvider")
  return ctx
}
