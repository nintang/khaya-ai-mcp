# GhanaNLP MCP Server

A Model Context Protocol (MCP) server that provides access to [GhanaNLP](https://ghananlp.org) APIs for African language processing, including:

- **Translation** - Translate between English and Ghanaian/African languages
- **ASR (Automatic Speech Recognition)** - Convert speech audio to text
- **TTS (Text-to-Speech)** - Convert text to natural-sounding speech

## Supported Languages

| Language | Code | Translation | ASR | TTS |
|----------|------|-------------|-----|-----|
| English | en | ✅ (source/target) | - | - |
| Twi | tw | ✅ | ✅ | ✅ |
| Ewe | ee | ✅ | ✅ | ✅ |
| Ga | gaa | ✅ | ✅ | ✅ |
| Dagbani | dag | ✅ | ✅ | ✅ |
| Fante | fat | ✅ | ✅ | ✅ |
| Gurene | gur | ✅ | ✅ | ✅ |
| Kikuyu | ki | ✅ | ✅ | ✅ |
| Luo | luo | ✅ | ✅ | ✅ |
| Kimeru | mer | ✅ | ✅ | ✅ |

## Prerequisites

1. **Python 3.10+**
2. **GhanaNLP API Key** - Get your API key from [https://ghananlp.org](https://ghananlp.org)

## Installation

### From Source

```bash
# Clone or download this repository
cd ghananlp-mcp

# Install with pip
pip install -e .
```

### Using uv (recommended)

```bash
cd ghananlp-mcp
uv pip install -e .
```

## Configuration

Set your GhanaNLP API key as an environment variable:

```bash
export GHANANLP_API_KEY="your-api-key-here"
```

## Usage

### Running the Server

```bash
# Using the installed command
ghananlp-mcp

# Or using Python directly
python -m ghananlp_mcp.server
```

### Configuring with Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ghananlp": {
      "command": "ghananlp-mcp",
      "env": {
        "GHANANLP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Or if using uv:

```json
{
  "mcpServers": {
    "ghananlp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ghananlp-mcp", "ghananlp-mcp"],
      "env": {
        "GHANANLP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Configuring with Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "ghananlp": {
      "command": "ghananlp-mcp",
      "env": {
        "GHANANLP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### 1. `ghananlp_translate`

Translate text between English and Ghanaian/African languages.

**Parameters:**
- `text` (string, required): The text to translate
- `language_pair` (string, required): Language pair in format 'source-target'

**Supported language pairs:**
- English to African: `en-tw`, `en-ee`, `en-gaa`, `en-dag`, `en-fat`, `en-gur`, `en-ki`, `en-luo`, `en-mer`
- African to English: `tw-en`, `ee-en`, `gaa-en`, `dag-en`, `fat-en`, `gur-en`, `ki-en`, `luo-en`, `mer-en`

**Example:**
```json
{
  "text": "Hello, how are you?",
  "language_pair": "en-tw"
}
```

### 2. `ghananlp_asr`

Convert speech audio to text (Automatic Speech Recognition).

**Parameters:**
- `audio_base64` (string, required): Base64-encoded audio data (WAV or MP3 format)
- `language` (string, required): Target language code (`tw`, `ee`, `gaa`, `dag`, `fat`, `gur`, `ki`, `luo`, `mer`)

**Example:**
```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAA...",
  "language": "tw"
}
```

### 3. `ghananlp_tts`

Convert text to speech (Text-to-Speech).

**Parameters:**
- `text` (string, required): The text to convert to speech
- `language` (string, required): Language code (`tw`, `ee`, `gaa`, `dag`, `fat`, `gur`, `ki`, `luo`, `mer`)

**Example:**
```json
{
  "text": "Wo ho te sɛn?",
  "language": "tw"
}
```

**Output:** Returns base64-encoded audio data that can be saved as an MP3/WAV file.

## Example Conversations

### Translation
> **You:** Translate "Good morning, how did you sleep?" to Twi
>
> **Claude:** I'll translate that for you using the GhanaNLP translation tool.
> 
> **Translation (en-tw):**
> - Original: Good morning, how did you sleep?
> - Translated: Maakye, wo adae sɛn?

### Text-to-Speech
> **You:** Convert "Akwaaba" to speech in Twi
>
> **Claude:** I'll generate audio for "Akwaaba" in Twi. The audio has been generated and here's the base64-encoded audio data...

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Project Structure

```
ghananlp-mcp/
├── README.md
├── pyproject.toml
└── src/
    └── ghananlp_mcp/
        ├── __init__.py
        └── server.py
```

## API Reference

This MCP server uses the official GhanaNLP API:
- **Base URL:** `https://translation-api.ghananlp.org`
- **Documentation:** [https://ghananlp.org](https://ghananlp.org)

## Troubleshooting

### "Access denied due to missing subscription key"
Make sure you've set the `GHANANLP_API_KEY` environment variable with a valid API key.

### "Invalid language pair"
Check that you're using a supported language pair. See the table above for valid combinations.

### Audio not playing
The TTS tool returns base64-encoded audio. You need to decode it and save it to a file:

```python
import base64

audio_base64 = "..."  # The base64 string from the response
audio_data = base64.b64decode(audio_base64)

with open("output.mp3", "wb") as f:
    f.write(audio_data)
```

## License

MIT License

## Credits

- [GhanaNLP](https://ghananlp.org) - For providing the language APIs
- [Model Context Protocol](https://modelcontextprotocol.io) - The protocol specification
