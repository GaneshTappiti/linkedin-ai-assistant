import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { useApp } from "@/context/AppContext";
import { OutputDisplay } from "@/components/OutputDisplay";
import { Globe, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { extractPageText, generateLinkedinOutput } from "@/lib/localAgent";

const URLToPost = () => {
  const [url, setUrl] = useState("");
  const [notes, setNotes] = useState("");
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
    try {
      let articleText = "";
      try {
        articleText = await extractPageText(url);
      } catch {
        toast.info("Could not read article directly (likely CORS). Using URL + your notes.");
      }

      const generated = await generateLinkedinOutput(profile, "url", {
        url,
        articleText,
        notes,
      });

      setOutput(generated);
      toast.success("URL template ready. Tell me what you want!");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      toast.error(`Failed to convert URL: ${message}`);
    } finally {
      setIsGenerating(false);
    }
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

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Key Notes (recommended)</label>
          <Textarea
            placeholder="Paste article highlights here for better output when the site blocks browser access..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={4}
          />
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
