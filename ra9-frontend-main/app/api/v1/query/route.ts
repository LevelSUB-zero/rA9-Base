import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';
import { saveJob } from '@/lib/job-store'; // Import saveJob

// In-memory store for job payloads (for demonstration purposes)
// In a real application, consider a more robust, persistent store
// interface JobPayload { // Moved to job-store.ts
//   text: string;
//   // Add other relevant data if needed
// }
// const jobPayloads = new Map<string, JobPayload>(); // Removed in-memory map

export async function POST(req: Request) {
  try {
    const { sessionId, userId, text, mode, loopDepth, allowMemoryWrite } = await req.json();

    if (!text) {
      return new NextResponse(JSON.stringify({ error: 'Text (prompt) is required' }), {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    }

    const jobId = uuidv4();
    await saveJob(jobId, { sessionId, userId, text, mode, loopDepth, allowMemoryWrite }); // Save all QueryRequest parameters
    // console.log(`[Query API] Stored job ${jobId} with payload:`, jobPayloads.get(jobId)); // Removed logging related to in-memory map

    return new NextResponse(JSON.stringify({ jobId }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error in POST /api/v1/query:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}

// Export the map for use in other route handlers (e.g., stream and trace) // Removed as not needed
// export { jobPayloads };
