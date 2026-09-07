# LinkedIn AI Assistant (Local Frontend Only - No Backend Needed)

This project runs fully in VS Code as an open-source local app.

- No hosted backend
- No Lovable AI service
- No Ollama or external LLM needed
- Frontend-only React app
- All generation via direct integration

## How It Works

The app keeps your profile in browser localStorage. When you click "Generate", it shows a template in the UI that you can customize. The content is generated directly and integrated into the app.

For URL mode, the app tries to fetch and parse article text in-browser. If a site blocks browser access (CORS), you can paste key notes in the notes field.

## Prerequisites

- Node.js 18+
- npm

## Local Setup

1. Install dependencies:

```bash
npm install
```

2. Start frontend:

```bash
npm run dev
```

3. Open the local Vite URL shown in terminal (usually `http://localhost:8080`).

## Key Files

- `src/lib/localAgent.ts`: Content generation logic.
- `src/pages/CreatePost.tsx`: manual topic flow.
- `src/pages/URLToPost.tsx`: URL-to-post flow.
- `src/context/AppContext.tsx`: local profile and app state storage.

## Notes

- This is entirely frontend-only. No server routes are required.
- All content is generated and displayed in the browser.
- Your profile stays in localStorage locally.
