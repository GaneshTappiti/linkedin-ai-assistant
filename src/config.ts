/**
 * Local Configuration for LinkedIn AI Assistant
 * 
 * Customize these settings to match your local Ollama setup and preferences.
 * NO BACKEND SERVER REQUIRED - Everything runs locally in your browser.
 */

export const config = {
  // --- Ollama Settings ---
  ollama: {
    // URL where your Ollama server is running
    // Default: http://localhost:11434 (standard Ollama default)
    baseUrl: "http://localhost:11434",

    // Model to use for generation
    // Other options: "mistral" (faster, lower quality), "neural-chat" (smaller)
    // Run `ollama list` to see installed models
    model: "llama3.1",

    // Generation parameters
    temperature: 0.7, // 0-1: Higher = more creative, Lower = more factual
    topP: 0.9, // Nucleus sampling diversity
    topK: 40, // Top-K sampling
  },

  // --- Content Generation Settings ---
  generation: {
    // Max tokens for a single generation
    maxTokens: 2000,

    // Timeout (ms) before considering a request failed
    requestTimeout: 60000,

    // Fallback to local generation if Ollama fails
    useFallbackOnError: true,
  },

  // --- Browser Storage Settings ---
  storage: {
    // Key used to store profile in localStorage
    profileKey: "linkedin-profile",

    // Persist generated outputs in localStorage (set false to clear after reload)
    persistOutputs: true,
  },

  // --- UI / App Behavior ---
  app: {
    // Page title
    title: "LinkedIn AI Assistant (Local Only)",

    // Show debug info in console
    debugMode: false,

    // Default tone when generating posts
    defaultTone: "professional",
  },

  // --- Feature Flags ---
  features: {
    // Enable URL extraction (requires DOMParser, may fail on some sites)
    enableUrlExtraction: true,

    // Enable local cache of recently generated posts
    enableOutputCache: true,

    // Enable keyboard shortcuts (Cmd/Ctrl+Enter to generate)
    enableKeyboardShortcuts: true,
  },
};

export default config;
