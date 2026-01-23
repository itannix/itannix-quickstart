# Python Example

A Python voice client for ItanniX using aiortc for WebRTC support.

## Prerequisites

- Python 3.9+
- A registered Client ID from the [ItanniX Dashboard](https://app.itannix.com)
- System dependencies for aiortc (see below)

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install libavdevice-dev libavfilter-dev libopus-dev libvpx-dev pkg-config
```

**macOS:**
```bash
brew install ffmpeg opus libvpx
```

**Windows:**
Windows support is limited. Consider using WSL2 with Ubuntu.

## Installation

1. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python voice_client.py --client-id YOUR_CLIENT_ID
```

### Options

| Flag | Description |
|------|-------------|
| `--client-id` | Your Client ID (required) |
| `--client-secret` | Your client secret (auto-generated if not provided) |
| `--server-url` | API server URL (default: https://api.itannix.com) |
| `--duration` | Connection duration in seconds (default: 60) |

### Examples

```bash
# First time (generates secret)
python voice_client.py --client-id d4f8e2a1-3b7c-4e9f-a5d6-1c2b3e4f5a6b

# With existing secret
python voice_client.py --client-id d4f8e2a1-3b7c-4e9f-a5d6-1c2b3e4f5a6b --client-secret your_saved_secret

# Custom duration
python voice_client.py --client-id YOUR_ID --duration 300
```

## Using as a Library

```python
import asyncio
from voice_client import VoiceClient

async def main():
    client = VoiceClient(
        client_id='your-client-id',
        client_secret='your-client-secret'
    )
    
    # Set up callbacks
    client.on_transcript = lambda text: print(f"You: {text}")
    client.on_assistant_message = lambda text: print(f"Assistant: {text}")
    client.on_function_call = lambda name, args, call_id: (
        print(f"Function: {name}({args})"),
        client.send_function_result(call_id, {'success': True})
    )
    
    await client.connect()
    await asyncio.sleep(60)
    await client.disconnect()

asyncio.run(main())
```

## Client-Side Functions

The client automatically handles these function calls:

| Function | Description |
|----------|-------------|
| `set_device_volume` | Set volume to 0-100% |
| `adjust_device_volume` | Increase/decrease volume by 10% |
| `quiet_device` | Mute audio |
| `stop_audio` | Stop audio playback |

Note: The default implementation just logs these calls. Implement actual volume control for your platform.

## Troubleshooting

**ModuleNotFoundError: No module named 'av'**
- Install system dependencies for ffmpeg/libav (see above)

**Microphone not detected**
- Check your audio input device is connected
- On Linux, ensure PulseAudio or ALSA is configured

**Connection failed: 401**
- Verify your Client ID is registered in the dashboard
- If using an existing secret, ensure it matches the enrolled secret
