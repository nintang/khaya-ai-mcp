"""
GhanaNLP MCP Server

Provides MCP tools for GhanaNLP APIs:
- Translation between English and Ghanaian languages
- ASR (Automatic Speech Recognition) - Speech to Text
- TTS (Text to Speech)

Supported languages:
- English (en)
- Twi (tw)
- Ga (gaa)
- Ewe (ee)
- Fante (fat)
- Dagbani (dag)
- Gurene (gur)
- Kikuyu (ki)
- Luo (luo)
- Kimeru (mer)
"""

import asyncio
import base64
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field


# API Configuration
BASE_URL = "https://translation-api.ghananlp.org"
API_KEY_HEADER = "Ocp-Apim-Subscription-Key"

# Supported language pairs for translation
TRANSLATION_PAIRS = [
    "en-tw",  # English to Twi
    "en-ee",  # English to Ewe
    "en-gaa", # English to Ga
    "en-dag", # English to Dagbani
    "en-fat", # English to Fante
    "en-gur", # English to Gurene
    "en-ki",  # English to Kikuyu
    "en-luo", # English to Luo
    "en-mer", # English to Kimeru
    "tw-en",  # Twi to English
    "ee-en",  # Ewe to English
    "gaa-en", # Ga to English
    "dag-en", # Dagbani to English
    "fat-en", # Fante to English
    "gur-en", # Gurene to English
    "ki-en",  # Kikuyu to English
    "luo-en", # Luo to English
    "mer-en", # Kimeru to English
]

# Supported languages for ASR
ASR_LANGUAGES = ["tw", "ee", "gaa", "dag", "fat", "gur", "ki", "luo", "mer"]

# Supported languages for TTS
TTS_LANGUAGES = ["tw", "ee", "gaa", "dag", "fat", "gur", "ki", "luo", "mer"]


def get_api_key() -> str:
    """Get API key from environment variable."""
    api_key = os.environ.get("GHANANLP_API_KEY")
    if not api_key:
        raise ValueError(
            "GHANANLP_API_KEY environment variable is required. "
            "Get your API key from https://ghananlp.org"
        )
    return api_key


class TranslateInput(BaseModel):
    """Input schema for translation."""
    text: str = Field(description="The text to translate")
    language_pair: str = Field(
        description=f"Language pair in format 'source-target'. Supported pairs: {', '.join(TRANSLATION_PAIRS)}"
    )


class ASRInput(BaseModel):
    """Input schema for speech-to-text."""
    audio_base64: str = Field(
        description="Base64-encoded audio data (WAV or MP3 format)"
    )
    language: str = Field(
        description=f"Target language code. Supported: {', '.join(ASR_LANGUAGES)}"
    )


class TTSInput(BaseModel):
    """Input schema for text-to-speech."""
    text: str = Field(description="The text to convert to speech")
    language: str = Field(
        description=f"Language code for speech synthesis. Supported: {', '.join(TTS_LANGUAGES)}"
    )


# Initialize MCP server
server = Server("ghananlp-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available GhanaNLP tools."""
    return [
        Tool(
            name="ghananlp_translate",
            description="""Translate text between English and Ghanaian/African languages.

Supported language pairs:
- English to: Twi (en-tw), Ewe (en-ee), Ga (en-gaa), Dagbani (en-dag), Fante (en-fat), Gurene (en-gur), Kikuyu (en-ki), Luo (en-luo), Kimeru (en-mer)
- To English: Twi (tw-en), Ewe (ee-en), Ga (gaa-en), Dagbani (dag-en), Fante (fat-en), Gurene (gur-en), Kikuyu (ki-en), Luo (luo-en), Kimeru (mer-en)

Example: Translate "Hello, how are you?" from English to Twi using language_pair="en-tw"
""",
            inputSchema=TranslateInput.model_json_schema(),
        ),
        Tool(
            name="ghananlp_asr",
            description="""Convert speech audio to text (Automatic Speech Recognition).

Transcribes audio files in Ghanaian/African languages to text.

Supported languages: Twi (tw), Ewe (ee), Ga (gaa), Dagbani (dag), Fante (fat), Gurene (gur), Kikuyu (ki), Luo (luo), Kimeru (mer)

Input: Base64-encoded audio data (WAV or MP3 format)
Output: Transcribed text in the specified language
""",
            inputSchema=ASRInput.model_json_schema(),
        ),
        Tool(
            name="ghananlp_tts",
            description="""Convert text to speech (Text-to-Speech).

Generates natural-sounding audio from text in Ghanaian/African languages.

Supported languages: Twi (tw), Ewe (ee), Ga (gaa), Dagbani (dag), Fante (fat), Gurene (gur), Kikuyu (ki), Luo (luo), Kimeru (mer)

Input: Text to synthesize and target language
Output: Base64-encoded audio data (can be saved as MP3/WAV file)
""",
            inputSchema=TTSInput.model_json_schema(),
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        api_key = get_api_key()
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

    if name == "ghananlp_translate":
        return await handle_translate(api_key, arguments)
    elif name == "ghananlp_asr":
        return await handle_asr(api_key, arguments)
    elif name == "ghananlp_tts":
        return await handle_tts(api_key, arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_translate(api_key: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle translation requests."""
    try:
        input_data = TranslateInput(**arguments)
    except Exception as e:
        return [TextContent(type="text", text=f"Invalid input: {str(e)}")]

    # Validate language pair
    if input_data.language_pair not in TRANSLATION_PAIRS:
        return [TextContent(
            type="text",
            text=f"Invalid language pair '{input_data.language_pair}'. Supported pairs: {', '.join(TRANSLATION_PAIRS)}"
        )]

    url = f"{BASE_URL}/v1/translate"
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        API_KEY_HEADER: api_key,
    }
    payload = {
        "in": input_data.text,
        "lang": input_data.language_pair,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            # The API typically returns the translation directly or in a specific field
            if isinstance(result, str):
                translated_text = result
            elif isinstance(result, dict):
                # Try common response field names
                translated_text = result.get("translation") or result.get("output") or result.get("text") or str(result)
            else:
                translated_text = str(result)

            return [TextContent(
                type="text",
                text=f"**Translation ({input_data.language_pair}):**\n\n"
                     f"**Original:** {input_data.text}\n\n"
                     f"**Translated:** {translated_text}"
            )]

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.text
        except:
            pass
        return [TextContent(
            type="text",
            text=f"API Error ({e.response.status_code}): {error_detail or str(e)}"
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_asr(api_key: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle speech-to-text requests."""
    try:
        input_data = ASRInput(**arguments)
    except Exception as e:
        return [TextContent(type="text", text=f"Invalid input: {str(e)}")]

    # Validate language
    if input_data.language not in ASR_LANGUAGES:
        return [TextContent(
            type="text",
            text=f"Invalid language '{input_data.language}'. Supported languages: {', '.join(ASR_LANGUAGES)}"
        )]

    # Decode base64 audio
    try:
        audio_data = base64.b64decode(input_data.audio_base64)
    except Exception as e:
        return [TextContent(type="text", text=f"Invalid base64 audio data: {str(e)}")]

    url = f"{BASE_URL}/asr/v1/transcribe"
    headers = {
        "Content-Type": "audio/mpeg",
        "Cache-Control": "no-cache",
        API_KEY_HEADER: api_key,
    }
    params = {"language": input_data.language}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, content=audio_data, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            # Extract transcription from response
            if isinstance(result, str):
                transcription = result
            elif isinstance(result, dict):
                transcription = result.get("transcription") or result.get("text") or result.get("output") or str(result)
            else:
                transcription = str(result)

            return [TextContent(
                type="text",
                text=f"**Speech-to-Text Transcription ({input_data.language}):**\n\n{transcription}"
            )]

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.text
        except:
            pass
        return [TextContent(
            type="text",
            text=f"API Error ({e.response.status_code}): {error_detail or str(e)}"
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_tts(api_key: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle text-to-speech requests."""
    try:
        input_data = TTSInput(**arguments)
    except Exception as e:
        return [TextContent(type="text", text=f"Invalid input: {str(e)}")]

    # Validate language
    if input_data.language not in TTS_LANGUAGES:
        return [TextContent(
            type="text",
            text=f"Invalid language '{input_data.language}'. Supported languages: {', '.join(TTS_LANGUAGES)}"
        )]

    url = f"{BASE_URL}/tts/v1/tts"
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        API_KEY_HEADER: api_key,
    }
    payload = {
        "text": input_data.text,
        "language": input_data.language,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # The response is audio binary data
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            # Determine audio format from content-type
            content_type = response.headers.get("content-type", "audio/mpeg")
            
            return [TextContent(
                type="text",
                text=f"**Text-to-Speech Audio Generated ({input_data.language}):**\n\n"
                     f"**Input Text:** {input_data.text}\n\n"
                     f"**Audio Format:** {content_type}\n\n"
                     f"**Audio Data (Base64):**\n```\n{audio_base64}\n```\n\n"
                     f"To use this audio, decode the base64 string and save it as an audio file (e.g., output.mp3)."
            )]

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.text
        except:
            pass
        return [TextContent(
            type="text",
            text=f"API Error ({e.response.status_code}): {error_detail or str(e)}"
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Main entry point."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
