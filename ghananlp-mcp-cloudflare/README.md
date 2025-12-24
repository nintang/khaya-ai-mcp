# GhanaNLP MCP Server - Cloudflare Workers

A Cloudflare Workers deployment of the GhanaNLP MCP server for Translation, ASR, and TTS.

## Features

- 🌍 **Translation** - English ↔ African languages (Twi, Ewe, Ga, Dagbani, Fante, etc.)
- 🎤 **ASR** - Speech-to-Text for African languages
- 🔊 **TTS** - Text-to-Speech for African languages
- ⚡ **Edge Deployment** - Fast global response times via Cloudflare's edge network
- 🔒 **Secure** - API key stored as Cloudflare secret

## Prerequisites

1. [Cloudflare account](https://dash.cloudflare.com/sign-up)
2. [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
3. [GhanaNLP API Key](https://ghananlp.org)

## Quick Start

### 1. Install Dependencies

```bash
cd ghananlp-mcp-cloudflare
npm install
```

### 2. Login to Cloudflare

```bash
npx wrangler login
```

### 3. Set Your API Key as a Secret

```bash
npx wrangler secret put GHANANLP_API_KEY
# Enter your API key when prompted
```

### 4. Deploy

```bash
npm run deploy
```

Your MCP server will be deployed to: `https://ghananlp-mcp.<your-subdomain>.workers.dev`

## Local Development

```bash
# Set API key for local dev
export GHANANLP_API_KEY="your-api-key"

# Start local dev server
npm run dev
```

## API Endpoints

### Health Check
```
GET /
GET /health
```

### MCP Protocol (JSON-RPC)
```
POST /mcp
Content-Type: application/json

{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
```

### Direct API Endpoints (for testing)

**Translate:**
```bash
curl -X POST https://your-worker.workers.dev/api/translate \
  -H "Content-Type: application/json" \
  -H "X-GhanaNLP-API-Key: your-api-key" \
  -d '{"text": "Hello, how are you?", "language_pair": "en-tw"}'
```

**Text-to-Speech:**
```bash
curl -X POST https://your-worker.workers.dev/api/tts \
  -H "Content-Type: application/json" \
  -H "X-GhanaNLP-API-Key: your-api-key" \
  -d '{"text": "Akwaaba", "language": "tw"}'
```

**Speech-to-Text:**
```bash
curl -X POST https://your-worker.workers.dev/api/asr \
  -H "Content-Type: application/json" \
  -H "X-GhanaNLP-API-Key: your-api-key" \
  -d '{"audio_base64": "...", "language": "tw"}'
```

## Using with Claude Desktop

Add to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ghananlp": {
      "transport": {
        "type": "http",
        "url": "https://ghananlp-mcp.your-subdomain.workers.dev/mcp"
      }
    }
  }
}
```

Or if using the Python local server with the Cloudflare worker as backend, you can create a proxy.

## MCP Tools

### ghananlp_translate
Translate between English and African languages.

```json
{
  "name": "ghananlp_translate",
  "arguments": {
    "text": "Good morning",
    "language_pair": "en-tw"
  }
}
```

### ghananlp_asr
Convert speech to text.

```json
{
  "name": "ghananlp_asr", 
  "arguments": {
    "audio_base64": "base64-encoded-audio",
    "language": "tw"
  }
}
```

### ghananlp_tts
Convert text to speech.

```json
{
  "name": "ghananlp_tts",
  "arguments": {
    "text": "Akwaaba",
    "language": "tw"
  }
}
```

## Supported Languages

| Language | Code | Translation | ASR | TTS |
|----------|------|-------------|-----|-----|
| English | en | ✅ | - | - |
| Twi | tw | ✅ | ✅ | ✅ |
| Ewe | ee | ✅ | ✅ | ✅ |
| Ga | gaa | ✅ | ✅ | ✅ |
| Dagbani | dag | ✅ | ✅ | ✅ |
| Fante | fat | ✅ | ✅ | ✅ |
| Gurene | gur | ✅ | ✅ | ✅ |
| Kikuyu | ki | ✅ | ✅ | ✅ |
| Luo | luo | ✅ | ✅ | ✅ |
| Kimeru | mer | ✅ | ✅ | ✅ |

## Custom Domain (Optional)

To use a custom domain:

1. Go to Cloudflare Dashboard → Workers & Pages → your worker
2. Click "Triggers" → "Custom Domains"
3. Add your domain (must be on Cloudflare DNS)

## Troubleshooting

### "Missing API key" error
Make sure you've set the secret:
```bash
npx wrangler secret put GHANANLP_API_KEY
```

Or pass it via header:
```bash
curl -H "X-GhanaNLP-API-Key: your-key" ...
```

### Deployment fails
Check you're logged in:
```bash
npx wrangler whoami
```

### View logs
```bash
npm run tail
```

## License

MIT
