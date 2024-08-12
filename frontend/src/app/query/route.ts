import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { query } = await request.json();

  // Here, you would typically make a request to your Python backend
  // For now, we'll just return a mock response
  const mockResults = [
    {
      text: "This is a sample result for: " + query,
      metadata: { source: "sample.pdf", page: 1 },
      image: null // In a real scenario, this would be a base64 encoded image
    }
  ];

  return NextResponse.json(mockResults);
}
