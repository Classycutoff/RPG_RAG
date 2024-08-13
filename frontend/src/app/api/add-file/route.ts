import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get('file') as File;

  if (!file) {
    return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
  }
  // Create a new FormData instance to send to the Python backend
  const backendFormData = new FormData();
  backendFormData.append('file', file);

  try {
    // Forward the file to the Python backend
    const backendResponse = await fetch('http://backend:5001/api/add-file', {
      method: 'POST',
      body: backendFormData,
    });

    if (!backendResponse.ok) {
      throw new Error('Failed to upload file to the Python backend.');
    }

    const backendData = await backendResponse.json();
    return NextResponse.json({ message: 'File uploaded successfully', ...backendData });
  } catch (error) {
    console.error('Error uploading file:', error);
    return NextResponse.json({ error: 'Failed to upload file' }, { status: 500 });
  }
}