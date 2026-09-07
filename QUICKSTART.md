# Quick Start: Run Locally in VS Code (2 min)

## 1️⃣ Prerequisites Check

Verify you have these installed:

```bash
node --version        # Should be 18+
npm --version         # Should be 9+
```

## 2️⃣ Install & Start the App

In the project folder:

```bash
npm install
npm run dev
```

You'll see:
```
Local:   http://localhost:8080/
```

## 3️⃣ Open in Browser

Click the URL or paste `http://localhost:8080` into your browser.

## 4️⃣ Use the App

### First Time: Set Your Profile
1. Click **"Your AI Profile"** in the left menu.
2. Fill in:
   - **Name**: Your actual name
   - **Bio**: e.g., "Founder @ Company | AI Enthusiast"
   - **Skills**: e.g., "AI, Startups, Product, Growth"
   - **Tone**: Pick your default (e.g., "Founder / Storytelling")
   - **Past Posts**: Paste 1-2 LinkedIn posts you wrote (helps tailor your voice)

3. Click **Save Profile**.

### Generate Posts

**Mode 1: Create from Idea**
1. Click **"Create Post from Idea"**.
2. Enter a **Topic** (e.g., "Why AI will disrupt content creation").
3. (Optional) Add **Context** with specific details.
4. Pick a **Tone** (or use your default).
5. Click **Generate Post**.
6. The app shows a template.
7. Tell me what you'd like and I'll generate the actual content you want you see in the app.

**Mode 2: Convert URL to Post**
1. Click **"Convert URL to Post"**.
2. Paste an article URL.
3. (Recommended) Paste key article excerpts in **"Key Notes"** field.
4. Click **"Convert to LinkedIn Post"**.
5. The app shows a template.
6. Tell me what you want and I'll generate the content for you.

---

## 📝 How It Works

When you click "Generate":
1. The app shows a template in the UI.
2. You tell me your topic or URL.
3. I generate the actual LinkedIn post content.
4. You see it live in the app.
5. Copy and use it directly on LinkedIn.

---

## 🎨 Output You Get

- **Hooks**: 3 attention-grabbing openers.
- **Post**: Full LinkedIn-ready post (300–500 words).
- **Hashtags**: 5–8 specific, non-generic tags.
- **Image Prompt**: Detailed description for image generation.

All content is **copied directly** to your clipboard—paste into LinkedIn, Notion, or your drafts.

---

## ⏱️ Tips

#### Faster Workflow
- Give me the topic or URL you want.
- I'll generate the exact content you want.
- You see it live in the app.

#### Better Output
- Share your **past posts** in the profile—helps tailor the voice.
- Add details in the **context** field (data, examples, personal stories).
- For URLs, **paste article excerpts** in the notes field.

#### Stuck?
- Restart the dev server: `Ctrl+C` then `npm run dev`.
- Make sure you're on `http://localhost:8080`.

---

## 📁 File Structure

```
linkedin-ai-assistant/
├── src/
│   ├── lib/
│   │   └── localAgent.ts       ← Generation logic
│   ├── pages/
│   │   ├── CreatePost.tsx       ← Manual topic flow
│   │   ├── URLToPost.tsx        ← URL-to-post flow
│   │   └── ProfileSetup.tsx     ← Profile settings
│   ├── context/
│   │   └── AppContext.tsx       ← Browser localStorage
│   └── components/
│       └── OutputDisplay.tsx    ← Shows generated content
├── package.json                 ← Dependencies (frontend-only)
├── vite.config.ts              ← Vite bundler config
└── README.md                    ← Full documentation
```

---

## ✅ Ready to Go

You now have a **frontend-only app** that:

- ✅ Runs in VS Code
- ✅ No backend server
- ✅ No external LLM required
- ✅ Fully open-source
- ✅ Your data stays local
- ✅ GitHub Copilot for editing

**Now just tell me what you want generated, and I'll show you the output in the app!** 🚀
