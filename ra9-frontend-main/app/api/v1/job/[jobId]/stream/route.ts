import { NextRequest } from 'next/server';
import { spawnCli } from '@/lib/cli-adapter';
import { getJob, deleteJob } from '@/lib/job-store';

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function toSseLine(obj: unknown): string {
  return `data: ${JSON.stringify(obj)}\n\n`;
}

function mapIterationPayload(input: any) {
  // Accept either { iteration: { iterationIndex, deltaSummary, ... } } or flat iteration fields
  const it = input?.iteration ?? input;
  const step = typeof it?.iterationIndex === 'number' ? it.iterationIndex : it?.step ?? 1;
  const summary = it?.deltaSummary ?? it?.summary ?? 'Iteration complete';
  const latencyMs = typeof it?.latencyMs === 'number' ? it.latencyMs : 0;
  const verified = typeof it?.verifier?.passed === 'boolean' ? it.verifier.passed : it?.verified ?? true;
  const id = it?.id ?? `iter-${step}`;
  const cost = typeof it?.cost === 'number' ? it.cost : null;
  return { type: 'iteration_complete', iteration: { id, step, summary, cost, latencyMs, verified } };
}

export async function GET(
  req: NextRequest,
  { params }: { params: { jobId: string } },
) {
  const { jobId } = await params;
  const jobPayload = await getJob(jobId);

  if (!jobPayload) {
    return new Response('Job not found', { status: 404 });
  }

  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const { stdout, kill, child } = spawnCli(jobPayload);

      req.signal.onabort = () => {
        kill();
        controller.close();
      };

      let buffer = '';
      let done = false;
      
      try {
        // Process stdout chunks
        for await (const chunk of stdout) {
          buffer += chunk.toString();
          let idx;
          while ((idx = buffer.indexOf('\n')) >= 0) {
            const line = buffer.slice(0, idx).trim();
            buffer = buffer.slice(idx + 1);
            if (!line) continue;
            try {
              const payload = JSON.parse(line);
              if (payload.kind === 'token') {
                const agent = payload.agent === 'system' || !payload.agent ? 'actor' : payload.agent;
                if (agent !== 'system') {
                  controller.enqueue(encoder.encode(toSseLine({ type: 'token', text: payload.token, agent })));
                }
              } else if (payload.kind === 'iteration_complete') {
                controller.enqueue(encoder.encode(toSseLine(mapIterationPayload(payload))));
              } else if (payload.kind === 'done') {
                controller.enqueue(encoder.encode(toSseLine({ type: 'done' })));
                done = true;
              } else if (payload.kind === 'error') {
                controller.enqueue(encoder.encode(toSseLine({ type: 'error', message: payload.message || 'unknown error' })));
              } else if (payload.type === 'meta_report') {
                controller.enqueue(encoder.encode(toSseLine({ type: 'meta_report', ...payload })))
              } else {
                controller.enqueue(encoder.encode(toSseLine(payload)));
              }
            } catch {
              controller.enqueue(encoder.encode(toSseLine({ type: 'token', text: line })));
            }
          }
        }
        
        // Wait for the Python process to actually complete
        await new Promise<void>((resolve) => {
          child.on('close', (code: number | null) => {
            console.log(`Python process exited with code ${code}`);
            resolve();
          });
        });
        
      } catch (error) {
        controller.enqueue(encoder.encode(toSseLine({ type: 'error', message: String(error) })));
        controller.error(error);
      } finally {
        kill();
        if (!done) {
          controller.enqueue(encoder.encode(toSseLine({ type: 'done' })));
        }
        controller.close();
        await deleteJob(jobId);
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  });
}
