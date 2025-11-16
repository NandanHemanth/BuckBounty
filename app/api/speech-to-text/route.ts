import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const audioFile = formData.get('audio') as Blob;

    if (!audioFile) {
      return NextResponse.json({ error: 'No audio file provided' }, { status: 400 });
    }

    // For now, return a message to use browser's built-in speech recognition
    // This will be handled on the client side
    return NextResponse.json({ 
      useBrowserSTT: true,
      text: 'Using browser speech recognition...' 
    });

  } catch (error) {
    console.error('Speech-to-text error:', error);
    return NextResponse.json(
      { error: 'Failed to transcribe audio', text: 'Error transcribing audio. Please try typing instead.' },
      { status: 500 }
    );
  }
}
