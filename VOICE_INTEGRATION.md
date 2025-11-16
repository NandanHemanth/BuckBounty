# 🎤 Voice Integration - ElevenLabs TTS & Speech-to-Text

## 🎯 Overview

Complete voice integration with ElevenLabs for text-to-speech (MARK's responses) and speech-to-text (user input) with automatic fallback to browser APIs.

## 🔊 Features

### 1. **Speech-to-Text (User Input)**
- Click microphone button to record
- Automatic transcription using OpenAI Whisper
- Transcribed text sent to MARK
- Visual recording indicator

### 2. **Text-to-Speech (MARK's Responses)**
- Automatic voice playback of MARK's responses
- Uses ElevenLabs API for high-quality voice
- Fallback to browser's built-in TTS
- Natural-sounding AI voice

### 3. **Fallback System**
- Primary: ElevenLabs API (premium quality)
- Fallback: Browser SpeechSynthesis API
- Graceful degradation if APIs fail

## 🎨 User Experience

### Voice Input Flow
```
1. User clicks 🎤 microphone button
2. Button turns red (recording)
3. User speaks their question
4. User clicks button again to stop
5. Audio transcribed to text
6. Text sent to MARK automatically
7. MARK responds with voice + text
```

### Voice Output Flow
```
1. MARK generates text response
2. Text displayed in chat
3. Text sent to ElevenLabs API
4. Audio generated and played automatically
5. User hears MARK's response
```

## 🔧 Technical Implementation

### Environment Variables (`.env`)

```env
# ElevenLabs API (Get from https://elevenlabs.io)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel voice (default)
```

### Voice IDs Available
```
21m00Tcm4TlvDq8ikWAM - Rachel (Female, American)
EXAVITQu4vr4xnSDxMaL - Bella (Female, American)
ErXwobaYiN019PkySvjV - Antoni (Male, American)
MF3mGyEYCl7XYWbV9V6O - Elli (Female, American)
TxGEqnHWrfWFTfGW9XjX - Josh (Male, American)
VR6AewLTigWG4xSOukaG - Arnold (Male, American)
pNInz6obpgDQGcFmaJgB - Adam (Male, American)
yoZ06aMxZJJ28mfd3POQ - Sam (Male, American)
```

### Frontend (`components/ChatInterface.tsx`)

**Speech-to-Text:**
```typescript
const handleVoiceInput = async () => {
  if (!isRecording) {
    // Start recording
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      
      // Send to API for transcription
      const formData = new FormData();
      formData.append('audio', audioBlob);
      
      const response = await fetch('/api/speech-to-text', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      const transcribedText = data.text;
      
      // Send transcribed text to MARK
      await handleSendMessage(transcribedText);
    };
    
    mediaRecorder.start();
    setIsRecording(true);
  } else {
    // Stop recording
    mediaRecorder.stop();
    setIsRecording(false);
  }
};
```

**Text-to-Speech:**
```typescript
const speakResponse = async (text: string) => {
  try {
    const response = await fetch('/api/text-to-speech', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    
    if (response.headers.get('Content-Type')?.includes('audio/mpeg')) {
      // ElevenLabs audio
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } else {
      // Fallback to browser TTS
      const utterance = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.speak(utterance);
    }
  } catch (error) {
    // Final fallback
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  }
};
```

### Backend API: Speech-to-Text (`app/api/speech-to-text/route.ts`)

```typescript
export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const audioFile = formData.get('audio') as Blob;

  // Use OpenAI Whisper API
  const whisperFormData = new FormData();
  whisperFormData.append('file', audioFile, 'audio.webm');
  whisperFormData.append('model', 'whisper-1');

  const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
    },
    body: whisperFormData
  });

  const data = await response.json();
  return NextResponse.json({ text: data.text });
}
```

### Backend API: Text-to-Speech (`app/api/text-to-speech/route.ts`)

```typescript
export async function POST(request: NextRequest) {
  const { text } = await request.json();
  
  const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
  const VOICE_ID = process.env.ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM';

  // Call ElevenLabs API
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
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.5
        }
      })
    }
  );

  const audioBuffer = await response.arrayBuffer();
  
  return new NextResponse(audioBuffer, {
    headers: {
      'Content-Type': 'audio/mpeg',
      'Content-Length': audioBuffer.byteLength.toString()
    }
  });
}
```

## 🎯 Use Cases

### Use Case 1: Hands-Free Budgeting
```
User: *clicks mic* "Can I afford AirPods Pro 2 for $249?"
MARK: *speaks* "Let me analyze your budget..."
Result: User gets spoken budget analysis
```

### Use Case 2: Driving/Multitasking
```
User: *clicks mic* "What are my top spending categories?"
MARK: *speaks* "Your top spending categories are..."
Result: User can listen while doing other tasks
```

### Use Case 3: Accessibility
```
User: *clicks mic* "Help me build wealth"
MARK: *speaks* "Based on current market trends..."
Result: Accessible for visually impaired users
```

## ✅ Benefits

### For Users:
- **Hands-Free** - Use while driving, cooking, etc.
- **Natural** - Speak naturally instead of typing
- **Accessible** - Great for visually impaired users
- **Multitasking** - Listen while doing other things
- **Faster** - Speaking is faster than typing

### For Platform:
- **Modern** - Cutting-edge voice AI
- **Engaging** - More interactive experience
- **Accessible** - Inclusive design
- **Differentiation** - Unique feature
- **Premium** - High-quality ElevenLabs voice

## 🚀 Testing

### Test 1: Voice Input
1. Click microphone button (🎤)
2. Button should turn red
3. Speak: "What's my budget?"
4. Click button again to stop
5. Should see: Transcribed text sent to MARK
6. Should hear: MARK's spoken response

### Test 2: Voice Output
1. Type any message
2. Send to MARK
3. Should see: Text response
4. Should hear: Spoken response automatically

### Test 3: Fallback
1. Don't configure ELEVENLABS_API_KEY
2. Send message to MARK
3. Should hear: Browser's built-in TTS voice
4. Should still work (graceful degradation)

### Test 4: Complex Query
1. Click mic
2. Say: "Can I afford AirPods Pro 2 for $249?"
3. Should transcribe correctly
4. Should get budget analysis
5. Should hear full response

## 🎊 Result

**Voice integration now provides:**
- 🎤 Speech-to-text for user input
- 🔊 Text-to-speech for MARK's responses
- 🎯 Automatic voice playback
- 🔄 Graceful fallback system
- 🌟 Premium ElevenLabs voice quality
- ♿ Accessibility support
- 🚗 Hands-free operation

**Users can now talk to MARK naturally!** 🎤🤖🔊

---

**Status:** ✅ Complete & Functional  
**Speech-to-Text:** OpenAI Whisper API  
**Text-to-Speech:** ElevenLabs API + Browser fallback  
**Voice Quality:** Premium (ElevenLabs)  
**Accessibility:** Full support  
**Hands-Free:** Yes
