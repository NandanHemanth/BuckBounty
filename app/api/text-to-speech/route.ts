import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { text } = await request.json();

    if (!text) {
      return NextResponse.json({ error: 'No text provided' }, { status: 400 });
    }

    const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
    const VOICE_ID = process.env.ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM'; // Default: Rachel voice

    if (!ELEVENLABS_API_KEY) {
      // Fallback to browser's built-in speech synthesis
      return NextResponse.json({ 
        error: 'ElevenLabs API key not configured',
        useBrowserTTS: true 
      }, { status: 200 });
    }

    // Analyze text for emotional context
    const hasExcitement = /!|great|amazing|excellent|wonderful|fantastic|congratulations/i.test(text);
    const hasWarning = /warning|caution|careful|important|urgent|overdue/i.test(text);
    const hasQuestion = /\?|should|would|could|can i/i.test(text);
    const hasNumbers = /\$|%|\d+/i.test(text);

    // Adjust voice settings based on content
    let stability = 0.5;
    let similarityBoost = 0.75;
    let style = 0.0;
    let useSpeakerBoost = true;

    if (hasExcitement) {
      // More expressive for exciting news
      stability = 0.3;
      similarityBoost = 0.8;
      style = 0.5; // More emotional
    } else if (hasWarning) {
      // More serious and clear for warnings
      stability = 0.7;
      similarityBoost = 0.6;
      style = 0.2;
    } else if (hasQuestion) {
      // Slightly more inquisitive
      stability = 0.4;
      similarityBoost = 0.7;
      style = 0.3;
    } else if (hasNumbers) {
      // Clear and precise for financial data
      stability = 0.6;
      similarityBoost = 0.7;
      style = 0.1;
    }

    // Call ElevenLabs API with enhanced settings
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
      {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': ELEVENLABS_API_KEY
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_multilingual_v2', // Better model for emotions
          voice_settings: {
            stability: stability,
            similarity_boost: similarityBoost,
            style: style,
            use_speaker_boost: useSpeakerBoost
          }
        })
      }
    );

    if (!response.ok) {
      throw new Error('ElevenLabs API request failed');
    }

    const audioBuffer = await response.arrayBuffer();
    
    return new NextResponse(audioBuffer, {
      headers: {
        'Content-Type': 'audio/mpeg',
        'Content-Length': audioBuffer.byteLength.toString()
      }
    });

  } catch (error) {
    console.error('Text-to-speech error:', error);
    return NextResponse.json(
      { error: 'Failed to generate speech', useBrowserTTS: true },
      { status: 500 }
    );
  }
}
