#!/usr/bin/env node

/**
 * Start Script for LinkedIn AI Assistant
 *
 * This script checks if Ollama is running, then starts the Vite dev server.
 * Run with: npm run start-local
 *
 * Or manually:
 *   1. Terminal 1: ollama serve
 *   2. Terminal 2: npm run dev
 */

const http = require("http");
const { spawn } = require("child_process");

const OLLAMA_URL = "http://localhost:11434";
const CHECK_INTERVAL = 1000;
const MAX_RETRIES = 10;

function checkOllama(retries = 0) {
  return new Promise((resolve, reject) => {
    const req = http.get(OLLAMA_URL, (res) => {
      if (res.statusCode === 200 || res.statusCode === 404) {
        resolve(true);
      } else {
        reject(new Error(`Ollama returned status ${res.statusCode}`));
      }
    });

    req.on("error", () => {
      if (retries < MAX_RETRIES) {
        console.log(
          `⏳ Waiting for Ollama (${retries + 1}/${MAX_RETRIES})... Make sure 'ollama serve' is running.`
        );
        setTimeout(() => {
          checkOllama(retries + 1).then(resolve).catch(reject);
        }, CHECK_INTERVAL);
      } else {
        reject(
          new Error(
            "❌ Ollama is not running. Please start it with: ollama serve"
          )
        );
      }
    });

    req.end();
  });
}

async function main() {
  console.log("🚀 LinkedIn AI Assistant - Local Setup");
  console.log("=======================================\n");

  try {
    console.log("Checking Ollama connection...");
    await checkOllama();
    console.log("✅ Ollama is running on localhost:11434\n");

    console.log("Starting Vite dev server...\n");
    const vite = spawn("npm", ["run", "dev"], {
      stdio: "inherit",
      shell: true,
    });

    vite.on("error", (error) => {
      console.error("❌ Failed to start dev server:", error);
      process.exit(1);
    });

    vite.on("exit", (code) => {
      process.exit(code);
    });
  } catch (error) {
    console.error(`\n❌ Startup Error:\n${error.message}\n`);
    console.log("Quick fix:");
    console.log("  1. Open a new terminal");
    console.log('  2. Run: ollama serve');
    console.log("  3. Then re-run this script\n");
    process.exit(1);
  }
}

main();
