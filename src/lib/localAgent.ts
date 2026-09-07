import { UserProfile, GeneratedOutput } from "@/context/AppContext";

type GenerateMode = "manual" | "url";

function normalizeHashtags(tags: string[]): string[] {
  return tags
    .map((tag) => tag.trim())
    .filter(Boolean)
    .map((tag) => (tag.startsWith("#") ? tag : `#${tag.replace(/\s+/g, "")}`));
}

function safeJsonParse<T>(value: string): T | null {
  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

function extractJsonBlock(text: string): string | null {
  const fenced = text.match(/```json\s*([\s\S]*?)```/i);
  if (fenced?.[1]) {
    return fenced[1].trim();
  }

  const first = text.indexOf("{");
  const last = text.lastIndexOf("}");
  if (first === -1 || last === -1 || first >= last) {
    return null;
  }

  return text.slice(first, last + 1);
}

function fallbackOutput(topicHint: string): GeneratedOutput {
  const normalizedTopic = topicHint || "your topic";
  return {
    hooks: [
      `Most people overcomplicate ${normalizedTopic}. Here is what actually works in practice.`,
      `I tested 3 approaches to ${normalizedTopic}. One clear winner emerged.`,
      `If you care about ${normalizedTopic}, this perspective will save you time.`,
    ],
    post: `I have been thinking deeply about ${normalizedTopic}.\n\nThe best results did not come from doing more. They came from doing the right things consistently.\n\nThree lessons stood out:\n1. Start with basics before optimization\n2. Keep your process simple and repeatable\n3. Share what works, not what sounds impressive\n\nWhat has worked best for you?`,
    hashtags: ["#LinkedIn", "#PersonalBrand", "#ContentStrategy", "#Leadership", "#Growth"],
    imagePrompt: `Editorial-style illustration of a professional sharing practical insights about ${normalizedTopic} on LinkedIn.`,
  };
}

function buildSystemPrompt(profile: UserProfile): string {
  return [
    "You are an expert LinkedIn ghostwriter.",
    "Write in high-signal, concise language.",
    "Avoid generic fluff and avoid repeating the input.",
    "Output must be JSON only with keys: hooks, post, hashtags, imagePrompt.",
    "hooks must contain exactly 3 unique strings.",
    "hashtags must contain 5 to 8 specific tags.",
    "Do not include markdown fences.",
    "",
    "User profile:",
    `Name: ${profile.name || "Unknown"}`,
    `Bio: ${profile.bio || ""}`,
    `Skills: ${profile.skills || ""}`,
    `Preferred tone: ${profile.tone || "professional"}`,
    `Past writing examples: ${profile.pastPosts || ""}`,
  ].join("\n");
}

function buildManualPrompt(input: { topic: string; context?: string; tone?: string }): string {
  return [
    "Task: Generate LinkedIn assets for manual idea input.",
    `Topic: ${input.topic}`,
    `Context: ${input.context || "None"}`,
    `Requested tone override: ${input.tone || "None"}`,
  ].join("\n");
}

function buildUrlPrompt(input: { url: string; articleText: string; notes?: string }): string {
  return [
    "Task: Generate LinkedIn assets from an article URL.",
    `URL: ${input.url}`,
    `User notes: ${input.notes || "None"}`,
    "",
    "Source article extract:",
    input.articleText || "No article text was available; infer from URL and notes.",
  ].join("\n");
}

async function generateContent(
  profile: UserProfile,
  mode: GenerateMode,
  input: { topic?: string; context?: string; tone?: string; url?: string; articleText?: string; notes?: string }
): Promise<string> {
  // This will be populated by the user/copilot
  // For now, return a placeholder that indicates content should be generated
  return JSON.stringify({
    hooks: [
      `Placeholder hook 1 - Tell me your topic and I'll generate this for you`,
      `Placeholder hook 2 - awaiting content`,
      `Placeholder hook 3 - awaiting content`,
    ],
    post: "Tell me what topic or URL you want, and I'll generate a complete LinkedIn post for you here.",
    hashtags: ["#LinkedIn", "#ContentStrategy", "#Placeholder"],
    imagePrompt: "Placeholder - I'll generate a specific image prompt when you provide content",
  });
}

function coerceOutput(rawText: string, topicHint: string): GeneratedOutput {
  const jsonBlock = extractJsonBlock(rawText);
  if (!jsonBlock) {
    return fallbackOutput(topicHint);
  }

  const parsed = safeJsonParse<GeneratedOutput>(jsonBlock);
  if (!parsed || !Array.isArray(parsed.hooks) || !Array.isArray(parsed.hashtags) || !parsed.post || !parsed.imagePrompt) {
    return fallbackOutput(topicHint);
  }

  return {
    hooks: parsed.hooks.slice(0, 3),
    post: parsed.post,
    hashtags: normalizeHashtags(parsed.hashtags).slice(0, 8),
    imagePrompt: parsed.imagePrompt,
  };
}

export async function extractPageText(url: string): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Unable to fetch URL (status ${response.status}).`);
  }

  const html = await response.text();
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  const paragraphNodes = Array.from(doc.querySelectorAll("article p, main p, p"));
  const text = paragraphNodes
    .map((node) => node.textContent?.trim() || "")
    .filter(Boolean)
    .join("\n");

  return text.slice(0, 4000);
}

export async function generateLinkedinOutput(
  profile: UserProfile,
  mode: GenerateMode,
  input: { topic?: string; context?: string; tone?: string; url?: string; articleText?: string; notes?: string }
): Promise<GeneratedOutput> {
  const system = buildSystemPrompt(profile);

  if (mode === "manual") {
    const topic = input.topic?.trim() || "";
    const prompt = buildManualPrompt({ topic, context: input.context, tone: input.tone });
    const result = await generateContent(profile, mode, input);
    return coerceOutput(result, topic);
  }

  const url = input.url?.trim() || "";
  const articleText = input.articleText || "";
  const prompt = buildUrlPrompt({ url, articleText, notes: input.notes });
  const result = await generateContent(profile, mode, input);
  return coerceOutput(result, url);
}
