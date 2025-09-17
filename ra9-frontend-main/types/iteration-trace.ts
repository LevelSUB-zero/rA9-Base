export type AgentOutput = {
  agent: "logical" | "creative" | "strategic" | "reflective"
  content: string
  confidence: number
  citations?: Array<{ source: string; ref: string }>
}

export type MemoryHit = { memoryId: string; score: number }

export type Iteration = {
  id: string
  iterationIndex: number
  timestamp: string
  agentOutputs: AgentOutput[]
  memoryHits: MemoryHit[]
  internalMetrics: { inferenceCost: number; latencyMs: number }
  verifierResult: { pass: boolean; notes?: string }
  deltaSummary: string
}

export type IterationTrace = {
  jobId: string
  iterations: Iteration[]
}
