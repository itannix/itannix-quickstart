#!/usr/bin/env python3
"""
ItanniX Voice Client for Python

A minimal WebRTC client for the ItanniX Realtime API using aiortc.

Requirements:
    pip install aiortc aiohttp

Usage:
    python voice_client.py --client-id YOUR_CLIENT_ID --client-secret YOUR_SECRET
"""

import asyncio
import argparse
import json
import logging
import secrets
import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRecorder, MediaBlackhole

# Try to import audio playback library
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_PLAYBACK_AVAILABLE = True
except ImportError:
    AUDIO_PLAYBACK_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceClient:
    """ItanniX Voice Client using WebRTC."""
    
    def __init__(self, client_id: str, client_secret: str, server_url: str = 'https://api.itannix.com', audio_device: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.server_url = server_url
        self.audio_device = audio_device  # e.g., ':1' for second audio device on macOS
        self.pc = None
        self.data_channel = None
        self.session = None
        
        # Callbacks
        self.on_transcript = None
        self.on_assistant_message = None
        self.on_function_call = None
    
    async def connect(self):
        """Connect to ItanniX and establish WebRTC session."""
        logger.info("Creating session...")
        
        # 1. Create session
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(
                f'{self.server_url}/v1/realtime/sessions',
                headers={
                    'Content-Type': 'application/json',
                    'X-Client-Id': self.client_id,
                    'X-Client-Secret': self.client_secret
                },
                json={'modalities': ['text', 'audio']}
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f'Session creation failed: {resp.status} - {error_text}')
                self.session = await resp.json()
        
        logger.info(f"Session created: {self.session.get('id', 'unknown')}")
        
        ice_servers = self.session.get('iceServers', [])
        
        # 2. Create peer connection
        config = {}
        if ice_servers:
            config['iceServers'] = ice_servers
        
        self.pc = RTCPeerConnection(configuration=config)
        
        # 3. Create data channel
        self.data_channel = self.pc.createDataChannel('messages', ordered=True)
        
        @self.data_channel.on('open')
        def on_open():
            logger.info("Data channel opened")
        
        @self.data_channel.on('message')
        def on_message(message):
            try:
                msg = json.loads(message)
                self._handle_message(msg)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON message: {message}")
        
        # 4. Add audio track (microphone)
        # Note: 'default' uses the system default audio input
        # On Linux, you may need to use 'pulse' format
        # On macOS, use 'avfoundation' format with ':N' where N is device index
        audio_added = False
        
        # If user specified a device, try it directly
        if self.audio_device:
            # Determine format based on device string
            if self.audio_device.startswith(':'):
                fmt = 'avfoundation'  # macOS
            elif self.audio_device.startswith('audio='):
                fmt = 'dshow'  # Windows
            else:
                fmt = 'pulse'  # Linux default
            
            try:
                player = MediaPlayer(self.audio_device, format=fmt)
                if player.audio:
                    self.pc.addTrack(player.audio)
                    logger.info(f"Using {fmt} with device '{self.audio_device}'")
                    audio_added = True
            except Exception as e:
                raise Exception(f"Failed to open audio device '{self.audio_device}': {e}")
        else:
            # Try different audio formats based on platform
            audio_formats = [
                ('default', 'pulse'),      # PulseAudio (Linux)
                ('default', 'alsa'),       # ALSA (Linux fallback)
                (':0', 'avfoundation'),    # macOS device 0
                (':1', 'avfoundation'),    # macOS device 1 (often built-in mic)
                (':default', 'avfoundation'),  # macOS default
                ('audio=default', 'dshow'),     # Windows
            ]
            
            for device, fmt in audio_formats:
                try:
                    player = MediaPlayer(device, format=fmt)
                    if player.audio:
                        self.pc.addTrack(player.audio)
                        logger.info(f"Using {fmt} with device '{device}'")
                        audio_added = True
                        break
                except Exception as e:
                    logger.debug(f"Failed to open audio with {fmt} device '{device}': {e}")
                    continue
        
        if not audio_added:
            raise Exception(
                "Could not open microphone. The ItanniX API requires audio input.\n"
                "Please check:\n"
                "  - A microphone is connected\n"
                "  - Required system packages are installed (see README)\n"
                "  - On Linux: PulseAudio or ALSA is running\n"
                "  - On macOS: Use --audio-device ':1' for built-in mic, ':0' for first device\n"
                "    List devices with: ffmpeg -f avfoundation -list_devices true -i \"\""
            )
        
        # 5. Handle remote audio - play to speakers
        self.audio_player_task = None
        
        @self.pc.on('track')
        def on_track(track):
            if track.kind == 'audio':
                logger.info("Received remote audio track - playing to speakers")
                if AUDIO_PLAYBACK_AVAILABLE:
                    self.audio_player_task = asyncio.create_task(self._play_audio_track(track))
                else:
                    logger.warning("Audio playback not available. Install sounddevice: pip install sounddevice numpy")
        
        # 6. Create offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        
        # Wait for ICE gathering to complete
        while self.pc.iceGatheringState != 'complete':
            await asyncio.sleep(0.1)
        
        logger.info("Sending SDP offer...")
        
        # 7. Send SDP to server
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(
                f'{self.server_url}/v1/realtime',
                headers={
                    'Content-Type': 'application/sdp',
                    'X-Client-Id': self.client_id,
                    'X-Client-Secret': self.client_secret
                },
                data=self.pc.localDescription.sdp
            ) as resp:
                # Accept both 200 and 201 as success
                if resp.status not in (200, 201):
                    error_text = await resp.text()
                    raise Exception(f'SDP exchange failed: {resp.status} - {error_text}')
                answer_sdp = await resp.text()
        
        # 8. Set remote description
        answer = RTCSessionDescription(sdp=answer_sdp, type='answer')
        await self.pc.setRemoteDescription(answer)
        
        logger.info("Connected to ItanniX!")
    
    async def _play_audio_track(self, track):
        """Play incoming audio track to speakers using sounddevice."""
        try:
            # Get default output device info
            logger.info(f"Audio output device: {sd.query_devices(kind='output')['name']}")
            
            # Open audio output stream - OpenAI Realtime API uses 24kHz
            stream = sd.OutputStream(
                samplerate=24000,
                channels=1,  # Mono audio
                dtype='int16',
                blocksize=480  # 20ms at 24kHz
            )
            stream.start()
            logger.info("Audio output stream started")
            
            frame_count = 0
            while True:
                try:
                    frame = await track.recv()
                    frame_count += 1
                    
                    # Convert audio frame to numpy array
                    audio_data = frame.to_ndarray()
                    
                    # Log first few frames for debugging
                    if frame_count <= 3:
                        logger.info(f"Audio frame {frame_count}: shape={audio_data.shape}, dtype={audio_data.dtype}")
                    
                    # Handle different array shapes - flatten to 1D for mono output
                    if audio_data.ndim == 2:
                        # Shape is (channels, samples) - flatten it
                        if audio_data.shape[0] == 1:
                            audio_data = audio_data[0]  # (1, 1920) -> (1920,)
                        elif audio_data.shape[0] == 2:
                            audio_data = audio_data[0]  # Take left channel from stereo
                        else:
                            audio_data = audio_data.flatten()
                    
                    # Ensure correct dtype
                    if audio_data.dtype != np.int16:
                        if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                            audio_data = (audio_data * 32767).astype(np.int16)
                        else:
                            audio_data = audio_data.astype(np.int16)
                    
                    stream.write(audio_data)
                except Exception as e:
                    error_type = type(e).__name__
                    if "MediaStreamError" in error_type or "ConnectionError" in error_type:
                        logger.info("Audio track ended")
                        break
                    logger.warning(f"Audio frame error ({error_type}): {e}")
                    continue
            
            stream.stop()
            stream.close()
            logger.info(f"Audio playback finished after {frame_count} frames")
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_message(self, message: dict):
        """Handle incoming messages from the data channel."""
        msg_type = message.get('type', '')
        
        # User transcript
        if msg_type == 'conversation.item.input_audio_transcription.completed':
            transcript = message.get('transcript', '')
            logger.info(f"You: {transcript}")
            if self.on_transcript:
                self.on_transcript(transcript)
            return
        
        # Assistant transcript (streaming)
        if msg_type == 'response.audio_transcript.delta':
            delta = message.get('delta', '')
            print(delta, end='', flush=True)
            return
        
        # Assistant transcript (complete)
        if msg_type == 'response.audio_transcript.done':
            transcript = message.get('transcript', '')
            print()  # New line after streaming
            logger.info(f"Assistant: {transcript}")
            if self.on_assistant_message:
                self.on_assistant_message(transcript)
            return
        
        # Function calls
        if msg_type == 'response.output_item.done':
            item = message.get('item', {})
            if item.get('type') == 'function_call':
                name = item.get('name', '')
                args_str = item.get('arguments', '{}')
                call_id = item.get('call_id', '')
                
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}
                
                logger.info(f"Function call: {name}({args})")
                
                # Handle client-side functions
                result = self._handle_local_function(name, args)
                if result is not None:
                    self.send_function_result(call_id, result)
                elif self.on_function_call:
                    self.on_function_call(name, args, call_id)
    
    def _handle_local_function(self, name: str, args: dict) -> dict | None:
        """Handle client-side function calls (volume control, etc.)."""
        if name == 'set_device_volume':
            level = args.get('volume_level', 50)
            logger.info(f"Setting volume to {level}%")
            # Implement actual volume control here
            return {'success': True, 'volume': level}
        
        if name == 'adjust_device_volume':
            action = args.get('action', 'increase')
            logger.info(f"Adjusting volume: {action}")
            # Implement actual volume control here
            return {'success': True, 'action': action}
        
        if name == 'quiet_device':
            logger.info("Muting device")
            # Implement actual mute here
            return {'success': True, 'volume': 0}
        
        if name == 'stop_audio':
            logger.info("Stopping audio")
            # Implement actual audio stop here
            return {'success': True, 'message': 'Audio stopped'}
        
        return None  # Not a local function
    
    def send_function_result(self, call_id: str, result: dict):
        """Send function call result back to the server."""
        if not self.data_channel or self.data_channel.readyState != 'open':
            logger.warning("Data channel not ready")
            return
        
        self.data_channel.send(json.dumps({
            'type': 'conversation.item.create',
            'item': {
                'type': 'function_call_output',
                'call_id': call_id,
                'output': json.dumps(result)
            }
        }))
        
        # Trigger response generation
        self.data_channel.send(json.dumps({
            'type': 'response.create'
        }))
    
    async def disconnect(self):
        """Close the connection."""
        if hasattr(self, 'audio_player_task') and self.audio_player_task:
            self.audio_player_task.cancel()
            try:
                await self.audio_player_task
            except asyncio.CancelledError:
                pass
        if self.data_channel:
            self.data_channel.close()
        if self.pc:
            await self.pc.close()
        logger.info("Disconnected")


async def main():
    parser = argparse.ArgumentParser(
        description='ItanniX Voice Client',
        epilog='List macOS audio devices: ffmpeg -f avfoundation -list_devices true -i ""'
    )
    parser.add_argument('--client-id', required=True, help='Your Client ID from the dashboard')
    parser.add_argument('--client-secret', help='Your client secret (auto-generated if not provided)')
    parser.add_argument('--server-url', default='https://api.itannix.com', help='API server URL')
    parser.add_argument('--duration', type=int, default=60, help='Connection duration in seconds')
    parser.add_argument('--audio-device', help='Audio device (macOS: ":0", ":1", etc. Linux: "default")')
    
    args = parser.parse_args()
    
    # Generate secret if not provided
    client_secret = args.client_secret or secrets.token_hex(32)
    if not args.client_secret:
        logger.info(f"Generated client secret: {client_secret}")
        logger.info("Save this secret for future connections!")
    
    client = VoiceClient(args.client_id, client_secret, args.server_url, args.audio_device)
    
    try:
        await client.connect()
        logger.info(f"Connected! Listening for {args.duration} seconds...")
        logger.info("Speak into your microphone to interact with the assistant.")
        await asyncio.sleep(args.duration)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
