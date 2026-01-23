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
from aiortc.contrib.media import MediaPlayer, MediaRecorder

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
        
        # 5. Handle remote audio
        @self.pc.on('track')
        def on_track(track):
            if track.kind == 'audio':
                logger.info("Received remote audio track")
                # You can record or play the audio here
                # Example: recorder = MediaRecorder('output.wav')
                # recorder.addTrack(track)
                # await recorder.start()
        
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
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f'SDP exchange failed: {resp.status} - {error_text}')
                answer_sdp = await resp.text()
        
        # 8. Set remote description
        answer = RTCSessionDescription(sdp=answer_sdp, type='answer')
        await self.pc.setRemoteDescription(answer)
        
        logger.info("Connected to ItanniX!")
    
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
