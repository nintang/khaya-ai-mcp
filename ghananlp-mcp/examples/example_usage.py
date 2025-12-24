#!/usr/bin/env python3
"""
Example script demonstrating how to use GhanaNLP APIs directly.
This is for testing purposes - the MCP server wraps these APIs.
"""

import asyncio
import base64
import os
import httpx


# Configuration
BASE_URL = "https://translation-api.ghananlp.org"
API_KEY = os.environ.get("GHANANLP_API_KEY", "your-api-key-here")


async def translate(text: str, language_pair: str) -> str:
    """Translate text between English and African languages."""
    url = f"{BASE_URL}/v1/translate"
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": API_KEY,
    }
    payload = {"in": text, "lang": language_pair}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


async def text_to_speech(text: str, language: str) -> bytes:
    """Convert text to speech."""
    url = f"{BASE_URL}/tts/v1/tts"
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": API_KEY,
    }
    payload = {"text": text, "language": language}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.content


async def speech_to_text(audio_data: bytes, language: str) -> str:
    """Convert speech audio to text."""
    url = f"{BASE_URL}/asr/v1/transcribe"
    headers = {
        "Content-Type": "audio/mpeg",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": API_KEY,
    }
    params = {"language": language}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, content=audio_data, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


async def main():
    """Run example usage."""
    print("GhanaNLP API Example Usage")
    print("=" * 50)

    # Example 1: Translation
    print("\n1. Translation (English to Twi)")
    print("-" * 30)
    try:
        result = await translate("Hello, how are you?", "en-tw")
        print(f"   Input: Hello, how are you?")
        print(f"   Output: {result}")
    except Exception as e:
        print(f"   Error: {e}")

    # Example 2: Text-to-Speech
    print("\n2. Text-to-Speech (Twi)")
    print("-" * 30)
    try:
        audio = await text_to_speech("Akwaaba", "tw")
        # Save to file
        with open("output_tts.mp3", "wb") as f:
            f.write(audio)
        print(f"   Input: Akwaaba")
        print(f"   Output: Saved to output_tts.mp3 ({len(audio)} bytes)")
    except Exception as e:
        print(f"   Error: {e}")

    # Example 3: Speech-to-Text (requires an audio file)
    print("\n3. Speech-to-Text")
    print("-" * 30)
    print("   (Requires an audio file - skipping in this example)")
    print("   To use: provide audio_data bytes and call speech_to_text(audio_data, 'tw')")

    print("\n" + "=" * 50)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
