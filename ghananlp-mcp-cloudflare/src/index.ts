/**
 * GhanaNLP MCP Server for Cloudflare Workers
 * 
 * Provides MCP tools for:
 * - Translation between English and African languages
 * - ASR (Speech-to-Text)
 * - TTS (Text-to-Speech)
 */

export interface Env {
  // Optional: Set a default API key (not recommended for public deployments)
  GHANANLP_API_KEY?: string;
  // Set to "true" to require users to provide their own API key
  REQUIRE_USER_API_KEY?: string;
}

// GhanaNLP API Configuration
const GHANANLP_BASE_URL = "https://translation-api.ghananlp.org";

// Supported languages
const TRANSLATION_PAIRS = [
  "en-tw", "en-ee", "en-gaa", "en-dag", "en-fat", "en-gur", "en-ki", "en-luo", "en-mer",
  "tw-en", "ee-en", "gaa-en", "dag-en", "fat-en", "gur-en", "ki-en", "luo-en", "mer-en"
];

const ASR_LANGUAGES = ["tw", "ee", "gaa", "dag", "fat", "gur", "ki", "luo", "mer"];
const TTS_LANGUAGES = ["tw", "ee", "gaa", "dag", "fat", "gur", "ki", "luo", "mer"];

// MCP Types
interface MCPRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface MCPResponse {
  jsonrpc: "2.0";
  id: string | number;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

interface Tool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

// Tool definitions
const TOOLS: Tool[] = [
  {
    name: "ghananlp_translate",
    description: `Translate text between English and Ghanaian/African languages.

Supported language pairs:
- English to: Twi (en-tw), Ewe (en-ee), Ga (en-gaa), Dagbani (en-dag), Fante (en-fat), Gurene (en-gur), Kikuyu (en-ki), Luo (en-luo), Kimeru (en-mer)
- To English: Twi (tw-en), Ewe (ee-en), Ga (gaa-en), Dagbani (dag-en), Fante (fat-en), Gurene (gur-en), Kikuyu (ki-en), Luo (luo-en), Kimeru (mer-en)`,
    inputSchema: {
      type: "object",
      properties: {
        text: { type: "string", description: "The text to translate" },
        language_pair: { 
          type: "string", 
          description: `Language pair (e.g., en-tw for English to Twi). Supported: ${TRANSLATION_PAIRS.join(", ")}`
        }
      },
      required: ["text", "language_pair"]
    }
  },
  {
    name: "ghananlp_asr",
    description: `Convert speech audio to text (Automatic Speech Recognition).

Supported languages: ${ASR_LANGUAGES.join(", ")}

Input: Base64-encoded audio data (WAV or MP3)
Output: Transcribed text`,
    inputSchema: {
      type: "object",
      properties: {
        audio_base64: { type: "string", description: "Base64-encoded audio data" },
        language: { 
          type: "string", 
          description: `Language code: ${ASR_LANGUAGES.join(", ")}`
        }
      },
      required: ["audio_base64", "language"]
    }
  },
  {
    name: "ghananlp_tts",
    description: `Convert text to speech (Text-to-Speech).

Supported languages: ${TTS_LANGUAGES.join(", ")}

Output: Base64-encoded audio data`,
    inputSchema: {
      type: "object",
      properties: {
        text: { type: "string", description: "Text to convert to speech" },
        language: { 
          type: "string", 
          description: `Language code: ${TTS_LANGUAGES.join(", ")}`
        }
      },
      required: ["text", "language"]
    }
  }
];

// GhanaNLP API calls
async function translateText(apiKey: string, text: string, langPair: string): Promise<string> {
  const response = await fetch(`${GHANANLP_BASE_URL}/v1/translate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-cache",
      "Ocp-Apim-Subscription-Key": apiKey
    },
    body: JSON.stringify({ in: text, lang: langPair })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Translation API error (${response.status}): ${error}`);
  }

  const result = await response.json();
  return typeof result === "string" ? result : JSON.stringify(result);
}

async function speechToText(apiKey: string, audioBase64: string, language: string): Promise<string> {
  const audioData = Uint8Array.from(atob(audioBase64), c => c.charCodeAt(0));

  const response = await fetch(`${GHANANLP_BASE_URL}/asr/v1/transcribe?language=${language}`, {
    method: "POST",
    headers: {
      "Content-Type": "audio/mpeg",
      "Cache-Control": "no-cache",
      "Ocp-Apim-Subscription-Key": apiKey
    },
    body: audioData
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`ASR API error (${response.status}): ${error}`);
  }

  const result = await response.json() as Record<string, unknown> | string;
  if (typeof result === "string") return result;
  if (typeof result === "object" && result !== null) {
    if ("transcription" in result) return String(result.transcription);
    if ("text" in result) return String(result.text);
  }
  return JSON.stringify(result);
}

async function textToSpeech(apiKey: string, text: string, language: string): Promise<string> {
  const response = await fetch(`${GHANANLP_BASE_URL}/tts/v1/tts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-cache",
      "Ocp-Apim-Subscription-Key": apiKey
    },
    body: JSON.stringify({ text, language })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`TTS API error (${response.status}): ${error}`);
  }

  const audioData = await response.arrayBuffer();
  const base64 = btoa(String.fromCharCode(...new Uint8Array(audioData)));
  return base64;
}

// Tool execution
async function executeTool(apiKey: string, name: string, args: Record<string, unknown>): Promise<unknown> {
  switch (name) {
    case "ghananlp_translate": {
      const text = args.text as string;
      const langPair = args.language_pair as string;
      
      if (!TRANSLATION_PAIRS.includes(langPair)) {
        throw new Error(`Invalid language pair '${langPair}'. Supported: ${TRANSLATION_PAIRS.join(", ")}`);
      }
      
      const translation = await translateText(apiKey, text, langPair);
      return {
        content: [{
          type: "text",
          text: `**Translation (${langPair}):**\n\n**Original:** ${text}\n\n**Translated:** ${translation}`
        }]
      };
    }

    case "ghananlp_asr": {
      const audioBase64 = args.audio_base64 as string;
      const language = args.language as string;
      
      if (!ASR_LANGUAGES.includes(language)) {
        throw new Error(`Invalid language '${language}'. Supported: ${ASR_LANGUAGES.join(", ")}`);
      }
      
      const transcription = await speechToText(apiKey, audioBase64, language);
      return {
        content: [{
          type: "text",
          text: `**Speech-to-Text Transcription (${language}):**\n\n${transcription}`
        }]
      };
    }

    case "ghananlp_tts": {
      const text = args.text as string;
      const language = args.language as string;
      
      if (!TTS_LANGUAGES.includes(language)) {
        throw new Error(`Invalid language '${language}'. Supported: ${TTS_LANGUAGES.join(", ")}`);
      }
      
      const audioBase64 = await textToSpeech(apiKey, text, language);
      return {
        content: [{
          type: "text",
          text: `**Text-to-Speech Audio Generated (${language}):**\n\n**Input Text:** ${text}\n\n**Audio Data (Base64):**\n\`\`\`\n${audioBase64}\n\`\`\`\n\nTo use: decode base64 and save as .mp3 or .wav file.`
        }]
      };
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// MCP Protocol Handler
async function handleMCPRequest(request: MCPRequest, apiKey: string): Promise<MCPResponse> {
  const { id, method, params } = request;

  try {
    switch (method) {
      case "initialize":
        return {
          jsonrpc: "2.0",
          id,
          result: {
            protocolVersion: "2024-11-05",
            capabilities: {
              tools: { listChanged: false }
            },
            serverInfo: {
              name: "ghananlp-mcp",
              version: "1.0.0"
            }
          }
        };

      case "notifications/initialized":
        return { jsonrpc: "2.0", id, result: {} };

      case "tools/list":
        return {
          jsonrpc: "2.0",
          id,
          result: { tools: TOOLS }
        };

      case "tools/call": {
        const toolParams = params as { name: string; arguments: Record<string, unknown> };
        const result = await executeTool(apiKey, toolParams.name, toolParams.arguments || {});
        return { jsonrpc: "2.0", id, result };
      }

      case "ping":
        return { jsonrpc: "2.0", id, result: {} };

      default:
        return {
          jsonrpc: "2.0",
          id,
          error: { code: -32601, message: `Method not found: ${method}` }
        };
    }
  } catch (error) {
    return {
      jsonrpc: "2.0",
      id,
      error: {
        code: -32000,
        message: error instanceof Error ? error.message : "Unknown error"
      }
    };
  }
}

// SSE Handler for streaming MCP
function createSSEStream(controller: ReadableStreamDefaultController<Uint8Array>) {
  const encoder = new TextEncoder();
  
  return {
    send(data: unknown) {
      const message = `data: ${JSON.stringify(data)}\n\n`;
      controller.enqueue(encoder.encode(message));
    },
    close() {
      controller.close();
    }
  };
}

// Main Worker Handler
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    };

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // Health check
    if (url.pathname === "/" || url.pathname === "/health") {
      const requireUserKey = env.REQUIRE_USER_API_KEY === "true";
      return new Response(JSON.stringify({
        status: "ok",
        service: "ghananlp-mcp",
        version: "1.0.0",
        auth: {
          mode: requireUserKey ? "user-provided" : "server-or-user",
          header: "X-GhanaNLP-API-Key",
          getApiKey: "https://ghananlp.org"
        },
        endpoints: {
          mcp: "/mcp",
          translate: "/api/translate",
          tts: "/api/tts",
          asr: "/api/asr"
        }
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }

    // Get API key - prioritize user-provided key
    const userApiKey = request.headers.get("X-GhanaNLP-API-Key");
    const requireUserKey = env.REQUIRE_USER_API_KEY === "true";
    
    let apiKey: string;
    
    if (requireUserKey) {
      // Mode 1: Users MUST provide their own API key (recommended for public deployments)
      if (!userApiKey) {
        return new Response(JSON.stringify({
          error: "API key required. Pass your GhanaNLP API key via X-GhanaNLP-API-Key header. Get one at https://ghananlp.org"
        }), {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
      apiKey = userApiKey;
    } else {
      // Mode 2: Use user key if provided, otherwise fall back to server key
      apiKey = userApiKey || env.GHANANLP_API_KEY || "";
      
      if (!apiKey) {
        return new Response(JSON.stringify({
          error: "Missing API key. Set GHANANLP_API_KEY secret or pass X-GhanaNLP-API-Key header."
        }), {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }

    // MCP JSON-RPC endpoint
    if (url.pathname === "/mcp") {
      if (request.method !== "POST") {
        return new Response("Method not allowed", { status: 405, headers: corsHeaders });
      }

      try {
        const mcpRequest = await request.json() as MCPRequest;
        const response = await handleMCPRequest(mcpRequest, apiKey);
        
        return new Response(JSON.stringify(response), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (error) {
        return new Response(JSON.stringify({
          jsonrpc: "2.0",
          id: null,
          error: { code: -32700, message: "Parse error" }
        }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }

    // SSE endpoint for MCP streaming
    if (url.pathname === "/sse") {
      const stream = new ReadableStream({
        async start(controller) {
          const sse = createSSEStream(controller);
          
          // Send initial connection message
          sse.send({
            jsonrpc: "2.0",
            method: "connection/ready",
            params: { serverInfo: { name: "ghananlp-mcp", version: "1.0.0" } }
          });

          // For SSE, we'll handle messages differently
          // This is a simplified version - full implementation would handle bidirectional comms
          if (request.method === "POST") {
            try {
              const mcpRequest = await request.json() as MCPRequest;
              const response = await handleMCPRequest(mcpRequest, apiKey);
              sse.send(response);
            } catch (e) {
              sse.send({
                jsonrpc: "2.0",
                id: null,
                error: { code: -32700, message: "Parse error" }
              });
            }
          }
          
          sse.close();
        }
      });

      return new Response(stream, {
        headers: {
          ...corsHeaders,
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive"
        }
      });
    }

    // Direct API endpoints for testing
    if (url.pathname === "/api/translate" && request.method === "POST") {
      try {
        const body = await request.json() as { text: string; language_pair: string };
        const result = await translateText(apiKey, body.text, body.language_pair);
        return new Response(JSON.stringify({ translation: result }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: String(error) }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }

    if (url.pathname === "/api/tts" && request.method === "POST") {
      try {
        const body = await request.json() as { text: string; language: string };
        const audioBase64 = await textToSpeech(apiKey, body.text, body.language);
        return new Response(JSON.stringify({ audio_base64: audioBase64 }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: String(error) }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }

    if (url.pathname === "/api/asr" && request.method === "POST") {
      try {
        const body = await request.json() as { audio_base64: string; language: string };
        const transcription = await speechToText(apiKey, body.audio_base64, body.language);
        return new Response(JSON.stringify({ transcription }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: String(error) }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }

    return new Response("Not found", { status: 404, headers: corsHeaders });
  }
};
