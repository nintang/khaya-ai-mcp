"""Tests for GhanaNLP MCP Server."""

import asyncio
import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from ghananlp_mcp.server import (
    server,
    list_tools,
    call_tool,
    handle_translate,
    handle_asr,
    handle_tts,
    TRANSLATION_PAIRS,
    ASR_LANGUAGES,
    TTS_LANGUAGES,
)


class TestListTools:
    """Test tool listing."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_three_tools(self):
        """Test that list_tools returns all three tools."""
        tools = await list_tools()
        assert len(tools) == 3
        tool_names = [t.name for t in tools]
        assert "ghananlp_translate" in tool_names
        assert "ghananlp_asr" in tool_names
        assert "ghananlp_tts" in tool_names

    @pytest.mark.asyncio
    async def test_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        tools = await list_tools()
        for tool in tools:
            assert tool.description is not None
            assert len(tool.description) > 0

    @pytest.mark.asyncio
    async def test_tools_have_input_schemas(self):
        """Test that all tools have input schemas."""
        tools = await list_tools()
        for tool in tools:
            assert tool.inputSchema is not None


class TestTranslation:
    """Test translation functionality."""

    @pytest.mark.asyncio
    async def test_translate_missing_api_key(self):
        """Test translation fails gracefully without API key."""
        with patch.dict(os.environ, {}, clear=True):
            if "GHANANLP_API_KEY" in os.environ:
                del os.environ["GHANANLP_API_KEY"]
            result = await call_tool("ghananlp_translate", {
                "text": "Hello",
                "language_pair": "en-tw"
            })
            assert len(result) == 1
            assert "GHANANLP_API_KEY" in result[0].text

    @pytest.mark.asyncio
    async def test_translate_invalid_language_pair(self):
        """Test translation fails with invalid language pair."""
        with patch.dict(os.environ, {"GHANANLP_API_KEY": "test-key"}):
            result = await call_tool("ghananlp_translate", {
                "text": "Hello",
                "language_pair": "invalid-pair"
            })
            assert len(result) == 1
            assert "Invalid language pair" in result[0].text

    @pytest.mark.asyncio
    async def test_translate_success(self):
        """Test successful translation."""
        mock_response = MagicMock()
        mock_response.json.return_value = "Wo ho te sɛn?"
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {"GHANANLP_API_KEY": "test-key"}):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                result = await call_tool("ghananlp_translate", {
                    "text": "How are you?",
                    "language_pair": "en-tw"
                })
                assert len(result) == 1
                assert "Translation" in result[0].text
                assert "How are you?" in result[0].text


class TestASR:
    """Test ASR (Speech-to-Text) functionality."""

    @pytest.mark.asyncio
    async def test_asr_invalid_language(self):
        """Test ASR fails with invalid language."""
        with patch.dict(os.environ, {"GHANANLP_API_KEY": "test-key"}):
            result = await call_tool("ghananlp_asr", {
                "audio_base64": "SGVsbG8=",  # "Hello" in base64
                "language": "invalid"
            })
            assert len(result) == 1
            assert "Invalid language" in result[0].text

    @pytest.mark.asyncio
    async def test_asr_invalid_base64(self):
        """Test ASR fails with invalid base64."""
        with patch.dict(os.environ, {"GHANANLP_API_KEY": "test-key"}):
            result = await call_tool("ghananlp_asr", {
                "audio_base64": "not-valid-base64!!!",
                "language": "tw"
            })
            assert len(result) == 1
            assert "Invalid base64" in result[0].text or "Error" in result[0].text


class TestTTS:
    """Test TTS (Text-to-Speech) functionality."""

    @pytest.mark.asyncio
    async def test_tts_invalid_language(self):
        """Test TTS fails with invalid language."""
        with patch.dict(os.environ, {"GHANANLP_API_KEY": "test-key"}):
            result = await call_tool("ghananlp_tts", {
                "text": "Hello",
                "language": "invalid"
            })
            assert len(result) == 1
            assert "Invalid language" in result[0].text


class TestLanguageConstants:
    """Test language constant definitions."""

    def test_translation_pairs_valid(self):
        """Test translation pairs are properly formatted."""
        for pair in TRANSLATION_PAIRS:
            parts = pair.split("-")
            assert len(parts) == 2
            # One should be English
            assert "en" in parts

    def test_asr_languages_not_empty(self):
        """Test ASR languages list is not empty."""
        assert len(ASR_LANGUAGES) > 0

    def test_tts_languages_not_empty(self):
        """Test TTS languages list is not empty."""
        assert len(TTS_LANGUAGES) > 0


class TestUnknownTool:
    """Test handling of unknown tools."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling unknown tool returns error."""
        with patch.dict(os.environ, {"GHANANLP_API_KEY": "test-key"}):
            result = await call_tool("unknown_tool", {})
            assert len(result) == 1
            assert "Unknown tool" in result[0].text
