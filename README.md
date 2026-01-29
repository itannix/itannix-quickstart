# ItanniX Quickstart Examples

Quickstart examples for integrating with the [ItanniX](https://itannix.com) voice AI platform.

## Examples

| Example | Framework | SDK | Description |
|---------|-----------|-----|-------------|
| [javascript-browser](./javascript-browser/) | Vanilla JS | None | Browser-based WebRTC client, no build step |
| [react](./react/) | React | [@itannix/react](https://github.com/itannix/itannix-sdk) | React app with Vite |
| [svelte](./svelte/) | Svelte | [@itannix/svelte](https://github.com/itannix/itannix-sdk) | Svelte app with Vite |
| [vue](./vue/) | Vue 3 | [@itannix/vue](https://github.com/itannix/itannix-sdk) | Vue app with Vite |

## Getting Started

### 1. Create an Account

Sign up at [app.itannix.com](https://app.itannix.com) to access the dashboard.

### 2. Create a Client

In the dashboard, go to **Clients** and create a new client. You'll get:
- **Client ID**: Identifies your application
- **Client Secret**: Used for authentication

### 3. Run an Example

```bash
# Clone this repo
git clone https://github.com/itannix/itannix-quickstart.git
cd itannix-quickstart

# Choose an example
cd react  # or svelte, vue, javascript-browser

# Install dependencies (not needed for javascript-browser)
npm install

# Run the app
npm run dev
```

Enter your Client ID and Secret in the app, then click Connect to start a voice conversation.

## What is ItanniX?

ItanniX provides a real-time voice AI API that lets you add conversational AI assistants to any application.

**Features:**
- Real-time voice conversations via WebRTC
- Low-latency speech-to-text and text-to-speech
- Custom assistant configuration via dashboard
- Function calling support for tool use
- Works on browsers, mobile, and IoT devices

## SDK

For production apps, use the official SDKs:

```bash
npm install @itannix/react   # React
npm install @itannix/svelte  # Svelte
npm install @itannix/vue     # Vue
```

See the [SDK documentation](https://github.com/itannix/itannix-sdk) for full API reference.

## Resources

- [Website](https://itannix.com)
- [Dashboard](https://app.itannix.com)
- [SDK Repository](https://github.com/itannix/itannix-sdk)
- [Documentation](https://itannix.com/docs)

## License

MIT - see [LICENSE](./LICENSE)
