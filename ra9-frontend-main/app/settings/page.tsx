"use client"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { useUIPrefs } from "@/components/ra9/ui-prefs"
import { logEvent } from "@/lib/telemetry-client"

export default function SettingsPage() {
  const {
    memoryConsentDefault,
    reducedMotion,
    highContrast,
    setMemoryConsentDefault,
    setReducedMotion,
    setHighContrast,
  } = useUIPrefs()

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">Settings & Privacy</h1>
        <p className="text-sm text-muted-foreground">Control memory policy, motion, and contrast preferences.</p>
      </header>

      <div className="ra9-card p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm">Default Memory Consent</div>
            <div className="text-xs text-muted-foreground">Require opt-in per query to write memory.</div>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              id="memory-consent"
              checked={memoryConsentDefault}
              onCheckedChange={(v) => {
                setMemoryConsentDefault(v)
                logEvent("prefs.default_memory_consent", { value: v })
              }}
            />
            <Label htmlFor="memory-consent" className="text-xs text-muted-foreground">
              Off / On
            </Label>
          </div>
        </div>

        <div className="mt-4 h-px w-full" style={{ background: "var(--ra9-border)" }} />

        <div className="mt-4 flex items-center justify-between">
          <div>
            <div className="text-sm">Reduced Motion</div>
            <div className="text-xs text-muted-foreground">Respect prefers-reduced-motion.</div>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              id="reduced-motion"
              checked={reducedMotion}
              onCheckedChange={(v) => {
                setReducedMotion(v)
                logEvent("prefs.reduced_motion", { value: v })
              }}
            />
            <Label htmlFor="reduced-motion" className="text-xs text-muted-foreground">
              Off / On
            </Label>
          </div>
        </div>

        <div className="mt-4 h-px w-full" style={{ background: "var(--ra9-border)" }} />

        <div className="mt-4 flex items-center justify-between">
          <div>
            <div className="text-sm">High Contrast</div>
            <div className="text-xs text-muted-foreground">Increase contrast for better readability.</div>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              id="high-contrast"
              checked={highContrast}
              onCheckedChange={(v) => {
                setHighContrast(v)
                logEvent("prefs.high_contrast", { value: v })
              }}
            />
            <Label htmlFor="high-contrast" className="text-xs text-muted-foreground">
              Off / On
            </Label>
          </div>
        </div>
      </div>
    </main>
  )
}
