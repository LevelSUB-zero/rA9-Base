export async function POST(req: Request) {
  try {
    const body = await req.json()
    // Keep it minimal for now; do not store PII
    console.log("[telemetry]", body?.type, body?.context?.ts)
  } catch (e) {
    console.log("[telemetry] invalid json")
  }
  return new Response(null, { status: 204 })
}
