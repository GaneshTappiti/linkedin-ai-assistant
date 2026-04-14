import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { useApp } from "@/context/AppContext";
import { OutputDisplay } from "@/components/OutputDisplay";
import { Sparkles } from "lucide-react";
import { toast } from "sonner";

const tones = [
  { value: "professional", label: "Professional" },
  { value: "founder", label: "Founder / Storytelling" },
  { value: "educational", label: "Educational" },
  { value: "inspirational", label: "Inspirational" },
  { value: "controversial", label: "Bold / Controversial" },
  { value: "casual", label: "Casual" },
];

const CreatePost = () => {
  const [topic, setTopic] = useState("");
  const [context, setContext] = useState("");
  const [tone, setTone] = useState("professional");
  const { profile, setOutput, isGenerating, setIsGenerating, output } = useApp();
  const navigate = useNavigate();

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error("Please enter a topic");
      return;
    }
    if (!profile.name) {
      toast.error("Set up your profile first for personalized results");
      navigate("/profile");
      return;
    }

    setIsGenerating(true);
    // Simulate AI generation (will be replaced with real edge function)
    setTimeout(() => {
      setOutput({
        hooks: [
          `Most people get ${topic} completely wrong. Here's what I learned after years in the trenches.`,
          `I spent 3 months studying ${topic}. The results changed everything.`,
          `Stop scrolling. If you care about ${topic}, this will save you months.`,
        ],
        post: `${context ? context + "\n\n" : ""}Here's my take on ${topic}:\n\nAfter working in ${profile.skills || "this space"} for years, I've noticed a pattern that most people miss.\n\nThe key insight? It's not about doing more — it's about doing the right things differently.\n\n3 lessons I've learned:\n\n1. Start with the fundamentals, not the trends\n2. Consistency beats intensity every single time\n3. Your unique perspective IS your competitive advantage\n\nThe bottom line: ${topic} isn't just another buzzword. It's a shift in how we think about value creation.\n\nWhat's your experience with this? Drop a comment below 👇`,
        hashtags: ["#LinkedIn", "#AI", `#${topic.replace(/\s+/g, "")}`, "#PersonalBrand", "#ContentCreator"],
        imagePrompt: `A modern, minimalist illustration showing a professional figure confidently sharing knowledge about ${topic}, with abstract tech elements and a warm gradient background in blue and purple tones. Clean, corporate style suitable for LinkedIn.`,
      });
      setIsGenerating(false);
    }, 2500);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Create Post from Idea</h1>
        <p className="text-muted-foreground text-sm mt-1">Enter your topic and let AI craft a LinkedIn-ready post.</p>
      </div>

      <Card className="p-6 space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Topic *</label>
          <Input
            placeholder="e.g. Why AI will replace 50% of marketing jobs"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Context (optional)</label>
          <Textarea
            placeholder="Add any specific details, data points, or personal experiences to include…"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            rows={4}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Tone</label>
          <Select value={tone} onValueChange={setTone}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {tones.map((t) => (
                <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button onClick={handleGenerate} disabled={isGenerating} className="w-full gap-2">
          <Sparkles className="h-4 w-4" />
          {isGenerating ? "Generating…" : "Generate Post"}
        </Button>
      </Card>

      <OutputDisplay />
    </div>
  );
};

export default CreatePost;
