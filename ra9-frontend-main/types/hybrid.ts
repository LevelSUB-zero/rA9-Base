export type JobId = string

export type Message = {
  id: string
  role: "user" | "ra9"
  content: string
  meta?: {
    loopDepth?: number
    confidenceAvg?: number
    iterations?: number
    citations?: { source: string; url: string; verified?: boolean }[]
  }
}

export type QueryRequest = {
  sessionId: string
  userId: string
  text: string
  mode: "concise" | "deep" | "debate" | "planner"
  loopDepth: number // 1..6
  allowMemoryWrite: boolean
}

export type Iteration = {
  iterationIndex: number
  timestamp: string
  agentOutputs: {
    agentName: "logical" | "creative" | "strategic" | "reflective"
    text: string
    confidence: number
    tokensRef?: string
  }[]
  memoryHits: { id: string; score: number }[]
  citations: { source: string; url: string }[]
  verifier: { passed: boolean; score?: number; notes?: string[] }
  deltaSummary: string
}

export type IterationTimelineProps = {
  iterations: Iteration[]
  onSelect: (index: number) => void
}

export type HybridComposerProps = {
  userId: string
  initialMode?: "concise" | "deep" | "debate" | "planner"
  defaultLoopDepth?: number // 1..6
  onSubmit: (req: QueryRequest) => Promise<JobId>
}

export type HybridChatStreamProps = {
  sessionId: string
  messages: Message[]
  liveJob?: JobId
  onInspectIteration: (iterationId: string) => void
}
