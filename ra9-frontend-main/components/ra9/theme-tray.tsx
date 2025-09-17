"use client"
import { useUIPrefs } from "./ui-prefs"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { logEvent } from "@/lib/telemetry-client"

export function ThemeTray() {
  const { reducedMotion, highContrast, setReducedMotion, setHighContrast } = useUIPrefs()
  return (
    <div
      className="fixed bottom-4 right-4 z-40 ra9-card"
      style={{ padding: "10px 12px" }}
      role="region"
      aria-label="Accessibility quick settings"
    >
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Switch
            id="tray-rm"
            checked={reducedMotion}
            onCheckedChange={(v) => {
              setReducedMotion(v)
              logEvent("ui.toggle_reduced_motion", { value: v })
            }}
            aria-label="Reduced motion"
          />
          <Label htmlFor="tray-rm" className="text-xs text-muted-foreground">
            Reduced motion
          </Label>
        </div>
        <div className="h-4 w-px" style={{ background: "var(--ra9-border)" }} />
        <div className="flex items-center gap-2">
          <Switch
            id="tray-hc"
            checked={highContrast}
            onCheckedChange={(v) => {
              setHighContrast(v)
              logEvent("ui.toggle_high_contrast", { value: v })
            }}
            aria-label="High contrast"
          />
          <Label htmlFor="tray-hc" className="text-xs text-muted-foreground">
            High contrast
          </Label>
        </div>
      </div>
    </div>
  )
}
