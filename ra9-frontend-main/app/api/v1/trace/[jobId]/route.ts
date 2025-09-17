import { NextResponse } from 'next/server';

export async function GET(
  _req: Request,
  { params }: { params: { jobId: string } },
) {
  const { jobId } = await params; // Await params here

  // In our current setup, iterations are not explicitly buffered on the frontend.
  // This is a placeholder for future implementation if detailed trace data is needed.
  const iterations: any[] = []; // Placeholder for actual buffered iterations

  return new NextResponse(JSON.stringify({ iterations }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}
