export type TelemetryContext = {
  ts: string
  url?: string
  ua?: string
  rm?: boolean
  hc?: boolean
  sid?: string
}

export type TelemetryEvent = {
  type: string
  payload?: Record<string, unknown>
  context?: TelemetryContext
}
