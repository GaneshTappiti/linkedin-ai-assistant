import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { useApp } from "@/context/AppContext";
import { OutputDisplay } from "@/components/OutputDisplay";
import { Globe, Sparkles } from "lucide-react";
import { toast } from "sonner";

const URLToPost = () => {
  const [url, setUrl] = useState("");
  const { profile, setOutput, isGenerating, setIsGenerating } = useApp();
  const navigate = useNavigate();

  const handleGenerate = async () => {
    if (!url.trim()) {
      toast.error("Please enter a URL");
      return;
    }
    if (!profile.name) {
      toast.error("Set up your profile first");
      navigate("/profile");
      return;
    }

    try {
      new URL(url);
    } catch {
      toast.error("Please enter a valid URL");
      return;
    }

    setIsGenerating(true);
    // Simulate (will be replaced with edge function)
    setTimeout(() => {
      const domain = new URL(url).hostname;
      setOutput({
        hooks: [
          `I just read this incredible article and had to share my take.`,
          `This article from ${domain} changed how I think about the future.`,
          `Everyone's talking about AI. But this article shows what nobody else sees.`,
        ],
        post: `Just came across a brilliant piece from ${domain} and it got me thinking.\n\nThe key insight that stood out:\n\nWe're moving from an era of information abundance to an era of attention scarcity. And this changes everything about how we build products, create content, and grow businesses.\n\nHere's what this means for you:\n\n→ Quality > Quantity (always)\n→ Your unique angle matters more than ever\n→ The winners will be those who can distill complexity into clarity\n\nAs someone working in ${profile.skills || "tech"}, I see this playing out daily.\n\nWhat's your take? Have you noticed this shift too?\n\n🔗 Link in comments`,
        hashtags: ["#LinkedIn", "#Insights", "#ThoughtLeadership", "#ContentStrategy", "#Innovation"],
        imagePrompt: `A sophisticated flat illustration of a professional reading and analyzing a digital article on a sleek tablet, with highlighted key insights floating around, modern blue gradient background, minimal corporate style for LinkedIn.`,
      });
      setIsGenerating(false);
    }, 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Convert URL to Post</h1>
        <p className="text-muted-foreground text-sm mt-1">Paste an article URL and get a LinkedIn post with your unique angle.</p>
      </div>

      <Card className="p-6 space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Article URL</label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="https://example.com/article"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </div>

        <Button onClick={handleGenerate} disabled={isGenerating} className="w-full gap-2">
          <Sparkles className="h-4 w-4" />
          {isGenerating ? "Analyzing & Generating…" : "Convert to LinkedIn Post"}
        </Button>
      </Card>

      <OutputDisplay />
    </div>
  );
};

export default URLToPost;
